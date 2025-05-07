import inspect
import json
import logging
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from satif_core import CodeExecutor, SDIFDatabase, Transformer
from satif_core.types import SDIFPath

from satif_sdk.code_executors import LocalCodeExecutor

logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Custom exception for export errors."""

    pass


# Global registry for decorated transformation functions
_TRANSFORMATION_REGISTRY = {}


class CodeTransformer(Transformer):
    """
    Executes custom Python code to transform data from an SDIF database into desired output files.

    It takes one or more SDIF files (representing standardized and adapted data),
    provides a unified SQLite connection to them, and runs user-defined Python logic
    to generate files.

    The transformation logic can be provided in several ways:
    - A Python function (decorated with @transformation or not)
    - A string containing Python code
    - A path to a Python script file

    The function should have one of these signatures:
    - def func(conn: sqlite3.Connection) -> Dict[str, Any]
    - def func(conn: sqlite3.Connection, context: Dict[str, Any]) -> Dict[str, Any]

    Args:
        function: The function, code string, or file path containing the transformation logic
        function_name: Name of the function to execute if using code string or file
        transform_schema: Optional schema for the transformation function
        code_executor: Optional custom code executor (defaults to LocalCodeExecutor)
        extra_context: Optional dictionary of objects to inject when executing the code

    Transformation Function Signature:
        The transform function should accept these parameters:
        - `conn` (sqlite3.Connection): A connection to an in-memory SQLite
          database with all input SDIF files attached as schemas.
        - `context` (Dict[str, Any], optional): Extra context values if needed.

        The function MUST return a dictionary (`Dict[str, Any]`) where:
        - Keys (str): Relative output filenames (e.g., "orders_extract.csv", "summary/report.json").
        - Values (Any): Data to write (e.g., `pandas.DataFrame`, `dict`, `list`, `str`, `bytes`).
          The file extension in the key typically determines the output format.

    Example:
        ```python
        from satif.transformers.code import transformation, CodeTransformer

        # Define a transformation with the decorator
        @transformation
        def process_orders(conn):
            df = pd.read_sql_query("SELECT * FROM db1.orders", conn)
            return {"processed_orders.csv": df}

        # Use the transformation
        transformer = CodeTransformer(function=process_orders)
        result_path = transformer.transform(
            sdif="orders.sdif",
            output_path="output/processed_orders.csv"
        )
        ```
    """

    def __init__(
        self,
        function: Union[Callable, str, Path],
        function_name: str = "transform",
        transform_schema: Optional[Dict[str, Any]] = None,
        code_executor: Optional[CodeExecutor] = None,
        extra_context: Optional[Dict[str, Any]] = None,
        db_schema_prefix: str = "db",
    ):
        self.transform_function_obj = None
        self.transform_code = None
        self.function_name = function_name
        self.transform_schema = transform_schema
        self.extra_context = extra_context or {}
        self.db_schema_prefix = db_schema_prefix
        self.function = function

        # Initialize code executor
        if code_executor is None:
            self.code_executor = LocalCodeExecutor()
        else:
            self.code_executor = code_executor

        # Internal state for output path, set during export
        self._current_output_path: Optional[Path] = None

        self._init_transform_function()

    def _init_transform_function(self):
        """Initialize the transformation function based on the input type."""
        function = self.function

        # Case 1: It's a callable function
        if callable(function):
            self.transform_function_obj = function
            # If it's a decorated function, use its registered name
            if hasattr(function, "_transform_name"):
                self.function_name = function._transform_name
            else:
                self.function_name = function.__name__

        # Case 2: It's a string (code or function name)
        elif isinstance(function, str):
            # Check if it's a registered function name
            if function in _TRANSFORMATION_REGISTRY:
                self.transform_function_obj = _TRANSFORMATION_REGISTRY[function]
                self.function_name = function
            else:
                # Assume it's code
                self.transform_code = function

        # Case 3: It's a Path to a Python file
        elif isinstance(function, Path):
            try:
                with open(function) as f:
                    self.transform_code = f.read()
            except Exception as e:
                raise ValueError(
                    f"Failed to read transformation function from file: {e}"
                ) from e
        else:
            raise TypeError("function must be a callable, string, or Path")

    def _load_transformation_function(self) -> Callable:
        """Executes the code string and retrieves the target transformation function."""
        execution_globals = {
            "pd": pd,
            "json": json,
            "Path": Path,
            "sqlite3": sqlite3,
            "datetime": datetime,
            "timedelta": timedelta,
            "SDIFDatabase": SDIFDatabase,
            "__builtins__": __builtins__,
            **self.extra_context,
        }
        execution_locals = {}

        try:
            # TODO: Use the code executor instead of compile()
            compiled_code = compile(
                self.transform_code, "<transformation_string>", "exec"
            )
            exec(compiled_code, execution_globals, execution_locals)
        except Exception as e:
            logger.exception("Error executing transformation code string:")
            raise ExportError(f"Error during transformation code execution: {e}") from e

        if self.function_name not in execution_locals:
            raise ExportError(
                f"Function '{self.function_name}' not found after executing the code string."
            )

        transform_func = execution_locals[self.function_name]
        if not callable(transform_func):
            raise ExportError(
                f"'{self.function_name}' defined in the code string is not a callable function."
            )

        return transform_func

    def _get_transformation_function(self) -> Callable:
        """Get or load the transformation function."""
        if self.transform_function_obj is not None:
            return self.transform_function_obj

        if self.transform_code is None:
            raise ExportError("No transformation code or function available")

        return self._load_transformation_function()

    def _execute_transformation(
        self,
        conn: sqlite3.Connection,
        should_close_conn: bool = True,
        attached_schemas: Dict[str, Path] = None,
    ) -> Dict[str, Any]:
        """
        Execute the transformation function with the given connection.

        Args:
            conn: SQLite connection to use
            should_close_conn: Whether we should close the connection after execution
            attached_schemas: Dictionary of schema names to paths (for cleanup)

        Returns:
            Dictionary of transformed data from the transformation function

        Raises:
            ExportError: If any error occurs during transformation function execution
        """
        if attached_schemas is None:
            attached_schemas = {}

        transform_func = self._get_transformation_function()
        logger.debug(f"Executing transformation function '{self.function_name}'")

        try:
            # Check function signature to decide how to call it
            sig = inspect.signature(transform_func)
            param_count = len(sig.parameters)

            if param_count == 1:
                # Function takes only connection
                result = transform_func(conn=conn)
            elif param_count >= 2:
                # Function takes connection and context
                result = transform_func(conn=conn, context=self.extra_context)
            else:
                # Invalid function signature
                raise ExportError(
                    "Transformation function must accept at least one parameter (conn)"
                )

            if not isinstance(result, dict):
                raise ExportError(
                    f"Transformation function '{self.function_name}' must return a dictionary, got {type(result)}"
                )

            # Ensure keys are strings
            return {str(k): v for k, v in result.items()}

        except Exception as e:
            logger.exception(
                f"Error during execution of the transformation function '{self.function_name}'"
            )
            raise ExportError(
                f"Error during transformation function execution ('{self.function_name}'): {e}"
            ) from e

    def _cleanup_connection(
        self,
        conn: sqlite3.Connection,
        attached_schemas: Dict[str, Path],
        should_close: bool,
    ) -> None:
        """
        Clean up database connection by detaching schemas and closing if needed.

        Args:
            conn: SQLite connection to clean up
            attached_schemas: Dictionary of schema names to paths to detach
            should_close: Whether to close the connection after detaching schemas
        """
        if conn is None:
            return

        for schema_name in attached_schemas:
            try:
                logger.debug(f"Detaching schema '{schema_name}'")
                conn.execute(f"DETACH DATABASE {schema_name};")
            except sqlite3.Error as e:
                logger.error(f"Error detaching database '{schema_name}': {e}")

        if should_close:
            try:
                logger.debug("Closing database connection.")
                conn.close()
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")

    def transform(
        self,
        sdif: Union[SDIFPath, List[SDIFPath], SDIFDatabase, Dict[str, SDIFPath]],
    ) -> Dict[str, Any]:
        """
        Transforms data from SDIF input(s) using the provided function and returns the in-memory data.

        Args:
            sdif: Input SDIF data source. Can be:
                  - A single path (str/Path)
                  - A list of paths
                  - An SDIFDatabase instance
                  - A dictionary mapping schema names to paths (e.g., {"customers": "customers.sdif"})

        Returns:
            Dictionary of transformed data where:
            - Keys (str): Relative output filenames (e.g., "orders_extract.csv", "summary/report.json").
            - Values (Any): Data to write (e.g., `pandas.DataFrame`, `dict`, `list`, `str`, `bytes`).

        Raises:
            ExportError: If any error occurs during transformation.
            ValueError: If input arguments are invalid.
            FileNotFoundError: If an input SDIF file does not exist.
            TypeError: If the 'sdif' argument is of an unsupported type.
        """
        # Handle the case where we receive an SDIFDatabase directly
        if isinstance(sdif, SDIFDatabase):
            try:
                schema_name = sdif.schema_name
                attached_schemas = {schema_name: Path(sdif.path)}
                return self._execute_transformation(
                    conn=sdif.conn,
                    should_close_conn=False,
                    attached_schemas=attached_schemas,
                )
            except Exception as e:
                if isinstance(
                    e,
                    (
                        ExportError,
                        FileNotFoundError,
                        ValueError,
                        TypeError,
                        NotImplementedError,
                    ),
                ):
                    raise e
                else:
                    raise ExportError(
                        f"Unexpected error during transformation: {e}"
                    ) from e

        # Process input SDIF paths
        input_paths: List[Path] = []
        input_schemas: Dict[str, Path] = {}

        # Handle different input types
        if isinstance(sdif, (str, Path)):
            path = Path(sdif).resolve()
            input_paths = [path]
            input_schemas = {f"{self.db_schema_prefix}{1}": path}
        elif isinstance(sdif, list):
            input_paths = [Path(p).resolve() for p in sdif]
            input_schemas = {
                f"{self.db_schema_prefix}{i + 1}": p for i, p in enumerate(input_paths)
            }
        elif isinstance(sdif, dict):
            # Use the provided schema names
            for schema_name, path in sdif.items():
                resolved_path = Path(path).resolve()
                input_paths.append(resolved_path)
                input_schemas[schema_name] = resolved_path
        else:
            raise TypeError(
                f"Unsupported type for 'sdif' argument: {type(sdif)}. "
                "Expected str, Path, list, dict, or SDIFDatabase."
            )

        if not input_paths:
            raise ValueError("No input SDIF paths found or provided.")

        # Validate paths exist before attaching
        for p in input_paths:
            if not p.exists() or not p.is_file():
                raise FileNotFoundError(f"Input SDIF file not found: {p}")

        conn: Optional[sqlite3.Connection] = None

        try:
            if len(input_paths) == 1 and len(input_schemas) == 1:
                path = input_paths[0]
                schema_name = next(iter(input_schemas.keys()))
                conn = sqlite3.connect(str(path))

                try:
                    conn.execute(f"ATTACH DATABASE ? AS {schema_name}", (str(path),))
                except sqlite3.Error as e:
                    self._cleanup_connection(conn, input_schemas, should_close=True)
                    raise ExportError(
                        f"Failed to attach '{path}' database as '{schema_name}': {e}"
                    ) from e

            else:
                # Multiple db case - create in-memory DB and attach all inputs
                logger.debug("Creating in-memory database for attaching inputs.")
                conn = sqlite3.connect(":memory:")

                for schema_name, path in input_schemas.items():
                    logger.debug(f"Attaching input {path} as schema '{schema_name}'")
                    try:
                        conn.execute(
                            f"ATTACH DATABASE ? AS {schema_name};", (str(path),)
                        )
                    except sqlite3.Error as e:
                        self._cleanup_connection(conn, input_schemas, should_close=True)
                        raise ExportError(
                            f"Failed to attach '{path}' database as '{schema_name}': {e}"
                        ) from e

            return self._execute_transformation(
                conn, should_close_conn=True, attached_schemas=input_schemas
            )

        except Exception as main_exp:
            logger.error(f"Transformation process failed: {main_exp}")
            if isinstance(
                main_exp,
                (
                    ExportError,
                    FileNotFoundError,
                    ValueError,
                    TypeError,
                    NotImplementedError,
                ),
            ):
                raise main_exp
            else:
                raise ExportError(
                    f"Unexpected error during transformation: {main_exp}"
                ) from main_exp

        finally:
            self._cleanup_connection(conn, input_schemas, should_close=True)

    def export(
        self,
        sdif: Union[SDIFPath, List[SDIFPath], SDIFDatabase, Dict[str, SDIFPath]],
        output_path: Union[str, Path] = Path("."),
        zip_archive: bool = False,
    ) -> Path:
        """
        Transforms data from SDIF input(s) and exports results to files.
        This is a convenience method that combines transform() and export().

        Args:
            sdif: Input SDIF data source. Can be:
                  - A single path (str/Path)
                  - A list of paths
                  - An SDIFDatabase instance
                  - A dictionary mapping schema names to paths (e.g., {"customers": "customers.sdif"})
            output_path: Path to the output file (if zip_archive=True or single output)
                         or directory (if multiple outputs). Defaults to current directory.
            zip_archive: If True, package all output files into a single ZIP archive
                         at the specified output_path.

        Returns:
            Path to the created output file or directory.

        Raises:
            ExportError: If any error occurs during transformation or writing.
            ValueError: If input arguments are invalid.
            FileNotFoundError: If an input SDIF file does not exist.
            TypeError: If the 'sdif' argument is of an unsupported type.
        """
        transformed_data = self.transform(sdif=sdif)
        return self._export_data(
            data=transformed_data, output_path=output_path, zip_archive=zip_archive
        )

    def _export_data(
        self,
        data: Dict[str, Any],
        output_path: Union[str, Path] = Path("."),
        zip_archive: bool = False,
    ) -> Path:
        """
        Exports the transformed data to files or a zip archive.

        Args:
            data: Dictionary of data to export where:
                 - Keys (str): Relative output filenames (e.g., "orders_extract.csv", "summary/report.json").
                 - Values (Any): Data to write (e.g., `pandas.DataFrame`, `dict`, `list`, `str`, `bytes`).
            output_path: Path to the output file (if zip_archive=True or single output)
                         or directory (if multiple outputs). Defaults to current directory.
            zip_archive: If True, package all output files into a single ZIP archive
                         at the specified output_path.

        Returns:
            Path to the created output file or directory.

        Raises:
            ExportError: If any error occurs during exporting or writing.
        """
        if not data:
            logger.warning("No data to export.")
            # Return the intended output path even if nothing was written
            return Path(output_path)

        resolved_output_path = Path(output_path).resolve()
        self._current_output_path = resolved_output_path  # Store for writing methods

        try:
            logger.debug(f"Exporting {len(data)} items to write.")

            if zip_archive:
                self._write_zip(data)
            else:
                self._write_files(data)

            return self._current_output_path

        except Exception as e:
            logger.error(f"Export process failed: {e}")
            if isinstance(e, ExportError):
                raise e
            else:
                raise ExportError(f"Unexpected error during export: {e}") from e

        finally:
            # Reset internal state
            self._current_output_path = None

    def _write_files(self, data_to_write: Dict[str, Any]) -> None:
        """Write exported data to individual files."""
        if self._current_output_path is None:
            raise ExportError(
                "Internal error: Output path not set before writing files."
            )
        output_path = self._current_output_path  # This is the path provided by the user

        target_dir: Path
        single_file_path: Optional[Path] = None

        if output_path.is_dir():
            # User provided an existing directory, write all files inside it
            target_dir = output_path
            logger.debug(
                f"Output path '{output_path}' is a directory. Writing files inside."
            )
        elif len(data_to_write) == 1 and (
            not output_path.exists() or output_path.is_file()
        ):
            # User provided a file path (or non-existent path) for a single output
            single_file_path = output_path
            target_dir = (
                output_path.parent
            )  # Files will be written relative to the parent
            logger.debug(f"Output path '{output_path}' treated as single file path.")
            # Ensure parent exists for the single file
            target_dir.mkdir(parents=True, exist_ok=True)
        elif len(data_to_write) > 1 and (not output_path.exists()):
            # User provided a non-existent path for multiple files, treat as directory
            target_dir = output_path
            logger.debug(
                f"Output path '{output_path}' does not exist. Creating as directory."
            )
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Ambiguous case: path exists, is a file, but multiple outputs requested
            # Or other unexpected scenarios.
            raise ExportError(
                f"Output path '{output_path}' is problematic. It exists but is not a directory, "
                f"and multiple output files ({len(data_to_write)}) were requested. "
                f"Provide a directory path or a non-existent path to create a directory."
            )

        # Now, write the files relative to the determined target_dir or as single_file_path
        for filename_str, data in data_to_write.items():
            if single_file_path:
                # Only one file, use the specific path determined earlier
                output_filepath = single_file_path
                # Optional: Warn if filename_str doesn't match single_file_path's name/extension?
            else:
                # Resolve filename within the target directory
                filename_part = Path(filename_str)
                # Basic check for unsafe components (e.g., '..', absolute paths)
                if ".." in filename_part.parts or filename_part.is_absolute():
                    logger.error(
                        f"Skipping potentially unsafe filename: {filename_str}"
                    )
                    continue

                output_filepath = (target_dir / filename_part).resolve()

                # Final check to ensure the path didn't escape the base directory
                # Use target_dir for the check
                if not str(output_filepath).startswith(str(target_dir.resolve())):
                    logger.error(
                        f"Skipping filename leading outside target directory '{target_dir}' after resolution: {filename_str}"
                    )
                    continue

            # Ensure parent directory exists (for cases like "subdir/file.csv")
            output_filepath.parent.mkdir(parents=True, exist_ok=True)

            try:
                self._write_single_file(output_filepath, data)
                logger.info(f"Successfully wrote output file: {output_filepath}")
            except Exception as e:
                # Raise ExportError for consistency in error handling upstream
                if isinstance(e, ExportError):
                    raise e
                raise ExportError(f"Error writing file {output_filepath}: {e}") from e

    def _write_zip(self, data_to_write: Dict[str, Any]) -> None:
        """Write exported data to a ZIP archive."""
        if self._current_output_path is None:
            raise ExportError("Internal error: Output path not set before writing zip.")
        output_path = self._current_output_path

        if output_path.is_dir():
            raise ExportError(
                f"Output path '{output_path}' must be a file path when zip_archive is True, but it is a directory."
            )
        # Optional: Check for .zip extension, could warn or force it.

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for filename, data in data_to_write.items():
                    # Use Path for manipulation, then convert to posix string for archive name
                    path_in_zip = Path(filename)
                    archive_name = path_in_zip.as_posix()

                    # Security checks for archive path
                    if ".." in path_in_zip.parts or path_in_zip.is_absolute():
                        logger.error(
                            f"Skipping potentially unsafe filename in zip: {filename}"
                        )
                        continue

                    content_bytes: Optional[bytes] = None
                    if isinstance(data, pd.DataFrame):
                        ext = path_in_zip.suffix.lower()
                        try:
                            if ext == ".csv":
                                content_bytes = data.to_csv(index=False).encode("utf-8")
                            elif ext == ".json":
                                content_bytes = data.to_json(
                                    orient="records", indent=2
                                ).encode("utf-8")
                            else:
                                # Default to CSV if extension is unknown/unsupported for DataFrame
                                logger.warning(
                                    f"Unsupported DataFrame extension '{ext}' in zip. Writing as CSV for '{filename}'"
                                )
                                archive_name = path_in_zip.with_suffix(
                                    ".csv"
                                ).as_posix()
                                content_bytes = data.to_csv(index=False).encode("utf-8")
                        except Exception as df_ex:
                            logger.error(
                                f"Error converting DataFrame '{filename}' for zip: {df_ex}"
                            )
                            continue  # Skip this file
                    elif isinstance(data, (dict, list)):
                        try:
                            content_bytes = json.dumps(data, indent=2).encode("utf-8")
                        except Exception as json_ex:
                            logger.error(
                                f"Error converting dict/list '{filename}' to JSON for zip: {json_ex}"
                            )
                            continue  # Skip this file
                    elif isinstance(data, str):
                        content_bytes = data.encode("utf-8")
                    elif isinstance(data, bytes):
                        content_bytes = data  # Already bytes
                    else:
                        logger.warning(
                            f"Unsupported data type {type(data)} for file '{filename}' in zip. Skipping."
                        )
                        continue  # Skip this file

                    # Write content bytes to zip if successfully generated
                    if content_bytes is not None:
                        try:
                            zipf.writestr(archive_name, content_bytes)
                        except Exception as zip_write_ex:
                            logger.error(
                                f"Error writing file '{archive_name}' to zip: {zip_write_ex}"
                            )
                            # Continue with other files

            logger.info(f"Successfully created ZIP archive: {output_path}")
        except Exception as e:
            # Catch errors like zipfile creation issues, permissions etc.
            raise ExportError(f"Error creating ZIP file {output_path}: {e}") from e

    def _write_single_file(self, filepath: Path, data: Any) -> None:
        """Helper to write data to a single file based on type."""
        # Reuse existing logic, ensure imports are present (openpyxl is conditional)
        try:
            if isinstance(data, pd.DataFrame):
                ext = filepath.suffix.lower()
                if ext == ".csv":
                    data.to_csv(filepath, index=False)
                elif ext == ".json":
                    data.to_json(filepath, orient="records", indent=2)
                elif ext in [".xlsx", ".xls"]:
                    try:
                        # Excel writing requires optional dependencies
                        if ext == ".xlsx":
                            import openpyxl  # Required for .xlsx  # noqa: F401
                        # else: # .xls might require xlwt, handle if needed
                        #     import xlwt
                        data.to_excel(filepath, index=False)
                    except ImportError:
                        dep = (
                            "openpyxl"
                            if ext == ".xlsx"
                            else "xlwt (for .xls, not auto-imported)"
                        )
                        logger.error(
                            f"Writing to {ext} requires '{dep}'. Please install it."
                        )
                        # Re-raise as ExportError for consistent handling
                        raise ExportError(
                            f"Missing dependency for {ext} export. Install '{dep}'."
                        )
                else:
                    # Default to CSV for unknown extensions for DataFrame
                    csv_path = filepath.with_suffix(".csv")
                    logger.warning(
                        f"Unsupported extension '{ext}' for DataFrame. Writing as CSV to {csv_path}"
                    )
                    data.to_csv(csv_path, index=False)
            elif isinstance(data, (dict, list)):
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            elif isinstance(data, str):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(data)
            elif isinstance(data, bytes):
                with open(filepath, "wb") as f:
                    f.write(data)
            else:
                # Raise TypeError directly if data type is fundamentally unsupported
                raise TypeError(
                    f"Unsupported data type for file '{filepath.name}': {type(data)}"
                )
        except Exception as e:
            # Catch file writing errors (permissions, disk space, etc.)
            # Re-raise as ExportError if not already one
            if isinstance(e, ExportError):
                raise e
            raise ExportError(f"Error writing data to file {filepath}: {e}") from e


def transformation(func=None, name=None):
    """
    Decorator to register a function as a transformation.

    Can be used with or without arguments:

    @transformation
    def my_transform(conn):
        ...

    @transformation(name="custom_name")
    def my_transform(conn):
        ...

    Args:
        func: The function to decorate
        name: Optional custom name for the transformation

    Returns:
        The decorated function
    """

    def decorator(f):
        # Use the function name if no custom name is provided
        transform_name = name or f.__name__
        _TRANSFORMATION_REGISTRY[transform_name] = f
        # Set attribute for easier identification
        f._is_transformation = True
        f._transform_name = transform_name
        return f

    if func is None:
        # Called with arguments: @transformation(name="...")
        return decorator
    else:
        # Called without arguments: @transformation
        return decorator(func)
