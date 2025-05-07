import logging
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import httpx
from satif_core import AsyncStandardizer
from satif_core.types import Datasource, SDIFPath

log = logging.getLogger(__name__)

# Configuration keys
ENV_REMOTE_BASE_URL = "SATIF_REMOTE_BASE_URL"
ENV_REMOTE_API_KEY = "SATIF_REMOTE_API_KEY"
ENV_REMOTE_ENDPOINT = "SATIF_REMOTE_ENDPOINT"
DEFAULT_ENDPOINT = "/standardize"  # Default API path
DEFAULT_TIMEOUT = 300.0  # Default timeout 5 minutes (httpx uses float)


class RemoteStandardizer(AsyncStandardizer):
    """
    A generic standardizer that sends datasource file(s) to a remote API
    for processing and receives the resulting SDIF file.

    Allows providing a custom `httpx.Client` instance for advanced configuration,
    otherwise creates a default client based on environment variables or parameters.
    Compresses multiple input files into a single zip archive before uploading.

    Requires configuration of the remote API base URL and potentially an API key.
    """

    # Dynamically set based on constructor argument or discovered plugins
    SUPPORTED_EXTENSIONS: Set[str] = set()

    _client: httpx.Client  # The client instance (provided or default)
    _endpoint_path: str  # Store endpoint path separately

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint_path: Optional[str] = None,
        supported_extensions: Optional[Union[List[str], Set[str]]] = None,
        timeout: Optional[float] = DEFAULT_TIMEOUT,  # httpx uses float
        client: Optional[httpx.Client] = None,
        **kwargs: Any,  # Allow additional config (e.g., passed to default client)
    ):
        """
        Initializes the remote standardizer.

        Args:
            base_url: The base URL of the remote standardization API.
                      Defaults to env {ENV_REMOTE_BASE_URL}. Used only if 'client' is not provided.
            api_key: The API key for authentication.
                     Defaults to env {ENV_REMOTE_API_KEY}. Used as Bearer token if 'client' is not provided.
            endpoint_path: Specific API endpoint path relative to the base URL.
                           Defaults to env {ENV_REMOTE_ENDPOINT} or '{DEFAULT_ENDPOINT}'.
            supported_extensions: A list or set of lowercase file extensions (including '.')
                                  this remote endpoint claims to support.
            timeout: Default request timeout in seconds. Used only if 'client' is not provided.
                     Defaults to {DEFAULT_TIMEOUT} seconds.
            client: An optional pre-configured `httpx.Client` instance. If provided,
                    `base_url`, `api_key`, and `timeout` args are ignored for client creation,
                    but `endpoint_path` is still used for the request URL.
            **kwargs: Additional keyword arguments passed to the default `httpx.Client` constructor
                      if `client` is not provided.
        """
        # Store configuration needed regardless of client source
        config_base_url = base_url or os.environ.get(ENV_REMOTE_BASE_URL)
        config_api_key = api_key or os.environ.get(ENV_REMOTE_API_KEY)
        self._endpoint_path = (
            endpoint_path or os.environ.get(ENV_REMOTE_ENDPOINT) or DEFAULT_ENDPOINT
        )

        # Set supported extensions for discovery
        type(self).SUPPORTED_EXTENSIONS = (
            set(ext.lower() for ext in supported_extensions)
            if supported_extensions
            else set()
        )

        if client:
            if not isinstance(client, httpx.Client):
                # Raise error early if incompatible client type is provided
                raise TypeError(
                    f"Expected client to be an instance of httpx.Client, got {type(client)}"
                )
            self._client = client
            log.debug(
                "Using provided httpx.Client instance. Base URL/Auth/Timeout args ignored."
            )
        else:
            # Create and configure a default client
            if not config_base_url:
                raise ValueError(
                    f"RemoteStandardizer requires a base_url if no client is provided, "
                    f"either via constructor argument or environment variable {ENV_REMOTE_BASE_URL}"
                )

            default_headers = self._prepare_default_headers(config_api_key)
            effective_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

            try:
                self._client = httpx.Client(
                    base_url=config_base_url,
                    headers=default_headers,
                    timeout=effective_timeout,
                    follow_redirects=True,  # Sensible default
                    **kwargs,  # Pass extra args like proxies, transport, limits etc.
                )
                log.debug(
                    f"Created default httpx.Client: base_url='{config_base_url}', timeout={effective_timeout}s"
                )
            except Exception as e:
                log.error(f"Failed to create default httpx.Client: {e}", exc_info=True)
                raise RuntimeError(
                    f"Failed to initialize default httpx client: {e}"
                ) from e

    def _prepare_default_headers(self, api_key: Optional[str]) -> Dict[str, str]:
        """Prepares standard request headers for the default client."""
        headers = {"Accept": "application/vnd.sqlite3"}  # Expecting SDIF back
        if api_key:
            # Assuming Bearer token auth, adjust if API uses something else
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _get_mimetype(self, file_path: Path) -> str:
        """Basic mimetype guessing."""
        ext = file_path.suffix.lower()
        if ext == ".csv":
            return "text/csv"
        if ext == ".xlsx":
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if ext == ".pdf":
            return "application/pdf"
        if ext == ".json":
            return "application/json"
        if ext == ".zip":
            return "application/zip"
        return "application/octet-stream"

    async def standardize(
        self,
        datasource: Datasource,
        output_path: SDIFPath,
        *,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> Path:
        """
        Performs standardization by calling the remote API using the configured httpx client.

        Compresses multiple input files into a zip archive before uploading.

        Args:
            datasource: Path or list of paths to the input file(s).
            output_path: The path where the resulting SDIF file should be saved.
            overwrite: If True, overwrite the output file if it exists.
            **kwargs: Optional parameters sent as form data in the request body
                      (e.g., specific processing instructions for the API).
                      Use `json=payload_dict` kwarg instead if API expects JSON payload.

        Returns:
            The path to the created SDIF database file.

        Raises:
            FileNotFoundError: If an input file doesn't exist.
            IOError: If file reading/writing fails.
            httpx.HTTPStatusError: For unsuccessful API responses (4xx, 5xx).
            ValueError: For configuration errors or unsupported operations.
            zipfile.BadZipFile: If zip creation fails.
        """
        output_path = Path(output_path)
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file exists and overwrite is False: {output_path}"
            )

        if isinstance(datasource, (str, Path)):
            input_paths = [Path(datasource)]
        elif isinstance(datasource, list) and datasource:
            input_paths = [Path(p) for p in datasource]
        else:
            raise ValueError("Invalid or empty datasource provided.")

        # Ensure all input files exist
        for p in input_paths:
            if not p.exists() or not p.is_file():
                raise FileNotFoundError(f"Input file not found or is not a file: {p}")

        # Target URL is relative to the client's base_url
        relative_url = self._endpoint_path.lstrip("/")

        files_to_upload: Dict[str, Any] = {}
        temp_zip_path: Optional[Path] = None

        try:
            # Prepare file(s) for upload
            if len(input_paths) == 1:
                upload_file_path = input_paths[0]
                upload_filename = upload_file_path.name
                upload_mimetype = self._get_mimetype(upload_file_path)
                log.debug(f"Preparing single file upload: {upload_filename}")
                files_to_upload["file"] = (
                    upload_filename,
                    open(upload_file_path, "rb"),
                    upload_mimetype,
                )
            elif len(input_paths) > 1:
                # Create a temporary zip file
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".zip"
                ) as tmp_zip:
                    temp_zip_path = Path(tmp_zip.name)
                log.info(
                    f"Compressing {len(input_paths)} files into temporary zip: {temp_zip_path}"
                )
                try:
                    with zipfile.ZipFile(
                        temp_zip_path, "w", zipfile.ZIP_DEFLATED
                    ) as zf:
                        for file_path in input_paths:
                            zf.write(
                                file_path, arcname=file_path.name
                            )  # Use original filename inside zip
                    upload_file_path = temp_zip_path
                    upload_filename = (
                        "datasource.zip"  # Standard name for zipped upload
                    )
                    upload_mimetype = "application/zip"
                    files_to_upload["file"] = (
                        upload_filename,
                        open(upload_file_path, "rb"),
                        upload_mimetype,
                    )
                except (OSError, zipfile.BadZipFile) as e:
                    raise RuntimeError(
                        f"Failed to create zip archive for upload: {e}"
                    ) from e
            else:  # Should not happen given checks above
                raise ValueError("No input files to process.")

            # Determine the full target URL for logging purposes (might be slightly inaccurate if client has complex routing)
            log_target_url = f"{str(self._client.base_url).rstrip('/')}/{relative_url}"
            log.info(f"Calling remote standardizer at {log_target_url}...")

            # Using 'data' for potential extra form fields, 'json' for JSON payload
            try:
                with (
                    self._client.stream(
                        "POST",
                        relative_url,
                        files=files_to_upload,  # httpx handles opening/closing files passed this way
                        data=kwargs,  # Pass extra args as form data
                        # Use json=payload_dict if API expects JSON alongside files
                    ) as response
                ):
                    response.raise_for_status()  # Raises httpx.HTTPStatusError for 4xx/5xx

                    log.info(
                        f"Receiving SDIF response from {log_target_url} (status: {response.status_code})..."
                    )
                    try:
                        with open(output_path, "wb") as f_out:
                            for chunk in (
                                response.iter_bytes()
                            ):  # Use iter_bytes for binary streaming
                                f_out.write(chunk)
                        log.info(
                            f"Successfully saved standardized SDIF file to {output_path}"
                        )
                    except OSError as e:
                        raise OSError(
                            f"Failed to write received SDIF file to {output_path}: {e}"
                        ) from e

            except httpx.HTTPStatusError as e:
                # More specific error for bad status codes
                log.error(
                    f"API request failed with status {e.response.status_code}: {e}",
                    exc_info=True,
                )
                error_detail = ""
                try:
                    # Attempt to get response text for debugging
                    content = e.response.read().decode("utf-8", errors="ignore")[:1024]
                    error_detail = f" - Response Body: {content}"
                except Exception:
                    pass  # Ignore errors reading response body
                raise RuntimeError(
                    f"API request to {log_target_url} failed with status {e.response.status_code}{error_detail}"
                ) from e
            except httpx.RequestError as e:
                # Catch other httpx request errors (network, timeout, etc.)
                log.error(
                    f"Remote standardization API request failed: {e}", exc_info=True
                )
                raise RuntimeError(
                    f"API request to {log_target_url} failed: {e}"
                ) from e
            except Exception as e:
                log.error(
                    f"Error during remote standardization process: {e}", exc_info=True
                )
                raise  # Re-raise other unexpected errors
        finally:
            # Ensure file handles opened manually (only the temp zip) are closed
            # httpx manages handles passed via 'files' dict
            if "file" in files_to_upload and temp_zip_path:
                file_tuple = files_to_upload["file"]
                if (
                    isinstance(file_tuple, tuple)
                    and len(file_tuple) > 1
                    and hasattr(file_tuple[1], "close")
                ):
                    try:
                        file_tuple[1].close()
                        log.debug("Closed temporary zip file handle after request.")
                    except Exception as close_err:
                        log.warning(f"Error closing temporary zip handle: {close_err}")
            # Clean up temporary zip file
            if temp_zip_path and temp_zip_path.exists():
                try:
                    temp_zip_path.unlink()
                    log.debug(f"Removed temporary zip file: {temp_zip_path}")
                except OSError as e:
                    log.warning(
                        f"Failed to remove temporary zip file {temp_zip_path}: {e}"
                    )

        return output_path
