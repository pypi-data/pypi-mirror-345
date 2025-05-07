from pathlib import Path
from typing import Optional

from satif_core import CodeExecutor, Standardizer
from satif_core.types import Datasource, SDIFPath

from satif_sdk.standardizers import get_standardizer


def standardize(
    datasource: Datasource,
    output_path: SDIFPath,
    *,  # Make subsequent arguments keyword-only
    standardizer: Optional[
        Standardizer
    ] = None,  # Option 1: Force a specific standardizer
    # Default (Option 2): If none of the above, use built-in standardizer based on file type.
    # (Option 3): if no built-in standardizer is available, we can use AIStandardizer
    artifact_dir: Optional[Path] = None,
    code_executor: Optional[
        CodeExecutor
    ] = None,  # TODO: Implement code_executor logic if needed by a standardizer
    overwrite: bool = False,
    **kwargs,
) -> Path:
    """
    Standardizes input datasource(s) into a single SDIF file.

    1. If standardizer is not provided, use the built-in standardizer based on the file type of the datasource.
    2. If standardizer is provided, use it to standardize the datasource.
    3. If no built-in standardizer is available, raise an error (AIStandardizer excluded for now).
    """
    chosen_standardizer: Optional[Standardizer] = None

    if standardizer:
        # Option 1: Use the provided standardizer instance
        chosen_standardizer = standardizer
    else:
        # Option 2: Find a built-in standardizer based on file type
        StandardizerClass = get_standardizer(datasource)
        if StandardizerClass:
            # Instantiate the found standardizer class.
            # Pass relevant parts of the config if needed, or handle config inside standardize method.
            # TODO: Determine if config needs to be passed to __init__ or standardize method
            chosen_standardizer = StandardizerClass(
                **(kwargs or {})
            )  # Pass config to constructor if it contains init args
        else:
            # No built-in standardizer found (and AIStandardizer is excluded)
            # Determine file extension(s) for a more informative error message
            extensions = set()
            if isinstance(datasource, (str, Path)):
                extensions.add(Path(datasource).suffix.lower())
            elif isinstance(datasource, list):
                for item in datasource:
                    try:
                        extensions.add(Path(item).suffix.lower())
                    except Exception:
                        pass  # Ignore invalid paths in list for error message
            raise ValueError(
                f"No suitable built-in standardizer found for this combination of file type(s): {', '.join(extensions) or 'unknown'}. "
                f"Please provide a standardizer instance."
            )

    if not chosen_standardizer:
        # This case should theoretically not be reached due to the logic above, but acts as a safeguard.
        raise RuntimeError("Failed to determine a standardizer to use.")

    result_path = chosen_standardizer.standardize(
        datasource=datasource,
        output_path=output_path,
        overwrite=overwrite,
    )

    return Path(result_path)
