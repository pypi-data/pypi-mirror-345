import datetime
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from satif_core import SDIFDatabase, Standardizer
from satif_core.types import Datasource, SDIFPath

# Constants
DEFAULT_SHEET = 0  # Default to the first sheet if none specified
DEFAULT_HEADER_ROW = 0
DEFAULT_SKIP_ROWS = 0

# Setup basic logging
log = logging.getLogger(__name__)


class XLSXStandardizer(Standardizer):
    """
    Standardizer for one or multiple Excel (.xlsx) files/sheets into an SDIF database.

    Transforms data from specified sheets within Excel files into the SDIF format.
    Default options (sheet_name/index, header_row, skip_rows, excluded_column_names)
    are set during initialization. These defaults can be overridden on a per-file basis
    when calling the `standardize` method using the `file_configs` parameter.
    Infers SQLite types (INTEGER, REAL, TEXT) from pandas dtypes.

    Attributes:
        default_sheet_name (Optional[Union[str, int]]): Default sheet identifier (name or 0-based index). If None, uses DEFAULT_SHEET (0).
        default_header_row (int): Default 0-based index for the header row.
        default_skip_rows (int): Default number of rows to skip *before* the header row.
        default_excluded_column_names (Set[str]): Default names of columns to exclude. Case-sensitive match against original header names.
        descriptions (Optional[Union[str, List[Optional[str]]]]): Descriptions for the data sources.
        table_names (Optional[Union[str, List[Optional[str]]]]): Target table names in the SDIF database.
        file_configs (Optional[Union[Dict[str, Any], List[Optional[Dict[str, Any]]]]]): File-specific configuration overrides.
    """

    def __init__(
        self,
        # Default parsing options (can be overridden by file_configs)
        sheet_name: Optional[
            Union[str, int]
        ] = None,  # Default behaviour: Use first sheet (index 0)
        header_row: int = DEFAULT_HEADER_ROW,
        skip_rows: int = DEFAULT_SKIP_ROWS,
        excluded_column_names: Optional[List[str]] = None,
        descriptions: Optional[Union[str, List[Optional[str]]]] = None,
        table_names: Optional[Union[str, List[Optional[str]]]] = None,
        file_configs: Optional[
            Union[Dict[str, Any], List[Optional[Dict[str, Any]]]]
        ] = None,
    ):
        """
        Initialize the XLSX standardizer with default and task-specific configurations.

        Args:
            sheet_name: Default sheet to read (name as str, 0-based index as int).
                        If None, defaults to the first sheet (index 0).
            header_row: Default 0-based row index to use as column headers.
            skip_rows: Default number of rows to skip at the beginning of the sheet *before* the header row.
            excluded_column_names: Default list of exact column header names to exclude.
            descriptions: A single description for all sources, or a list of
                          descriptions (one per input file expected in standardize).
                          If None, descriptions are omitted. Used for `sdif_sources.source_description`.
            table_names: A single table name (used as a base if multiple files),
                         a list of table names (one per input file expected in standardize), or None.
                         If None, table names are derived from sheet names (or filenames if sheet name unavailable).
            file_configs: Optional configuration overrides. Can be a single dict
                          applied to all files, or a list of dicts (one per file expected
                          in standardize, use None in list to apply defaults). Keys in the dict
                          can include 'sheet_name', 'header_row', 'skip_rows', 'excluded_column_names'.
                          These override the defaults set above for the specific file.
        """
        if header_row < 0:
            raise ValueError("header_row cannot be negative.")
        if skip_rows < 0:
            raise ValueError("skip_rows cannot be negative.")

        # Default settings (fallbacks)
        self.default_sheet_name = (
            sheet_name if sheet_name is not None else DEFAULT_SHEET
        )
        self.default_header_row = header_row
        self.default_skip_rows = skip_rows
        self.default_excluded_column_names = set(excluded_column_names or [])

        # Task-specific configurations
        self.descriptions = descriptions
        self.table_names = table_names
        self.file_configs = file_configs

    def _sanitize_name(self, name: str, prefix: str = "item") -> str:
        """Clean up a string to be a safe SQL identifier (snake_case)."""
        import re

        name = str(name).strip().lower()
        # Replace disallowed characters with underscore
        name = re.sub(
            r"[^\w\s-]", "", name
        ).strip()  # Keep alphanumeric, space, underscore, hyphen
        name = re.sub(r"[-\s]+", "_", name)  # Replace space/hyphen with underscore
        # Ensure it starts with a letter or underscore if not empty
        safe_name = "".join(c for c in name if c.isalnum() or c == "_")
        if safe_name and not (safe_name[0].isalpha() or safe_name[0] == "_"):
            safe_name = f"_{safe_name}"
        # Remove consecutive underscores
        safe_name = re.sub(r"_+", "_", safe_name)
        return safe_name or prefix  # Return prefix if name becomes empty

    def _map_pandas_dtype_to_sqlite(self, dtype: Any) -> str:
        """Maps pandas/numpy dtype to a suitable SQLite type."""
        if pd.api.types.is_integer_dtype(dtype):
            return "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            return "REAL"
        elif pd.api.types.is_bool_dtype(dtype):
            return "INTEGER"  # Store bools as 0 or 1
        elif pd.api.types.is_datetime64_any_dtype(
            dtype
        ) or pd.api.types.is_timedelta64_dtype(dtype):
            return "TEXT"  # Store datetime/timedelta as ISO 8601 strings
        else:
            return "TEXT"  # Default to TEXT for object, string, category, etc.

    def _prepare_value_for_sqlite(
        self, value: Any
    ) -> Union[str, int, float, bytes, None]:
        """Prepares a Python value for SQLite insertion based on its type."""
        if pd.isna(value):
            return None
        elif isinstance(value, (datetime.datetime, datetime.date, pd.Timestamp)):
            # Always convert datetime-like objects to ISO 8601 format string
            try:
                return value.isoformat()
            except AttributeError:
                # Handle cases like numpy datetime64 which might not have isoformat directly
                return str(value)
        elif isinstance(value, bool):
            return 1 if value else 0
        elif isinstance(value, (int, float, str, bytes)):
            return value  # Already compatible
        else:
            # For other types (e.g., lists, dicts, custom objects found in 'object' columns)
            # default to string representation. Consider JSON conversion for dicts/lists?
            # For now, keep it simple.
            return str(value)

    def standardize(
        self,
        datasource: Datasource,
        output_path: SDIFPath,
        *,  # Enforce keyword arguments for options
        overwrite: bool = False,
        config: Optional[
            Dict[str, Any]
        ] = None,  # From base class, currently unused here
        **kwargs,  # From base class, currently unused here
    ) -> Path:
        """
        Standardize one or more Excel files into a single SDIF database file.

        Reads a specified sheet from each input Excel file and stores its data
        in a corresponding table within the output SDIF database.

        Args:
            datasource: A single path or a list of paths to the input Excel file(s) (.xlsx).
            output_path: The path for the output SDIF database file.
            overwrite: If True, overwrite the output SDIF file if it exists.
            config: Optional configuration dictionary (from base class, currently unused).
            **kwargs: Additional keyword arguments (from base class, currently unused).

        Returns:
            The path to the created SDIF database file.

        Raises:
            ValueError: If input files are invalid, list arguments stored in the instance
                        have incorrect lengths compared to datasource, config values are invalid,
                        or pandas/database errors occur.
            FileNotFoundError: If an input Excel file does not exist.
            ImportError: If 'pandas' or 'openpyxl' is not installed.
            Exception: For errors during Excel parsing or database operations (specific exceptions may vary).
        """
        try:
            import openpyxl  # Check if engine is available
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                f"Missing dependency: {e}. Please install pandas and openpyxl (`pip install pandas openpyxl`)"
            ) from e

        output_path = Path(output_path)
        if isinstance(datasource, (str, Path)):
            input_paths = [Path(datasource)]
        else:
            input_paths = [Path(p) for p in datasource]

        num_inputs = len(input_paths)

        # --- Normalize List Arguments ---
        def normalize_list_arg(arg, arg_name, expected_len):
            if isinstance(arg, (str, dict)) or (
                isinstance(arg, list)
                and arg_name == "File configs"
                and isinstance(arg[0], dict)
                and len(arg) == 1  # Special case single dict config
            ):  # Single item applies to all
                return [arg] * expected_len
            elif isinstance(arg, list):
                if len(arg) != expected_len:
                    raise ValueError(
                        f"{arg_name} list length ({len(arg)}) must match "
                        f"input files count ({expected_len})."
                    )
                return arg
            elif arg is None:
                return [None] * expected_len
            else:  # single non-list, non-dict item
                return [arg] * expected_len

        processed_descriptions = normalize_list_arg(
            self.descriptions, "Descriptions", num_inputs
        )
        processed_table_names = normalize_list_arg(
            self.table_names, "Table names", num_inputs
        )
        processed_configs = normalize_list_arg(
            self.file_configs, "File configs", num_inputs
        )

        # --- Open SDIF Database ---
        with SDIFDatabase(output_path, overwrite=overwrite) as db:
            processed_table_basenames = {}  # Track base names to handle duplicates

            for i, input_path in enumerate(input_paths):
                if not input_path.exists():
                    raise FileNotFoundError(f"Input Excel file not found: {input_path}")
                if not input_path.is_file():
                    raise ValueError(f"Input path is not a file: {input_path}")
                if not input_path.suffix.lower() == ".xlsx":
                    log.warning(
                        f"Input file {input_path} does not have .xlsx extension. Attempting to read anyway."
                    )

                # --- Determine Effective Configuration ---
                current_config = processed_configs[i] or {}
                if not isinstance(current_config, dict):
                    raise ValueError(
                        f"File config item {i} must be a dictionary or None."
                    )

                current_sheet_name = current_config.get(
                    "sheet_name", self.default_sheet_name
                )
                current_header_row = current_config.get(
                    "header_row", self.default_header_row
                )
                current_skip_rows = current_config.get(
                    "skip_rows", self.default_skip_rows
                )
                # Combine default and file-specific exclusions
                current_excluded_names = self.default_excluded_column_names.union(
                    set(current_config.get("excluded_column_names", []))
                )
                current_description = processed_descriptions[i]
                current_input_table_name = processed_table_names[
                    i
                ]  # Name provided by user for this file

                if current_header_row < 0:
                    raise ValueError(
                        f"Configured header_row cannot be negative (file: {input_path.name})."
                    )
                if current_skip_rows < 0:
                    raise ValueError(
                        f"Configured skip_rows cannot be negative (file: {input_path.name})."
                    )

                # --- Read Excel Sheet ---
                try:
                    # skiprows in pandas skips rows *before* reading data, header is relative to *after* skiprows
                    # Our skip_rows means rows before the header row.
                    # Pandas: header is 0-indexed row *after* skipping rows.
                    # Example: skip_rows=1, header_row=0 means skip 1 row, header is the next row (original index 1).
                    # Example: skip_rows=0, header_row=1 means skip 0 rows, header is the second row (original index 1).
                    # So, pandas header = config header_row. Pandas skiprows = config skip_rows.
                    df = pd.read_excel(
                        input_path,
                        sheet_name=current_sheet_name,
                        header=current_header_row,
                        skiprows=current_skip_rows,
                        engine="openpyxl",
                        # Keep NaN values as is for now, convert later
                        keep_default_na=True,
                        na_values=None,  # Avoid pandas interpreting 'NA', 'NULL' etc. as NaN automatically
                    )

                    # Get the actual sheet name if an index was used
                    actual_sheet_name = current_sheet_name
                    if isinstance(current_sheet_name, int):
                        try:
                            xl = pd.ExcelFile(input_path, engine="openpyxl")
                            if 0 <= current_sheet_name < len(xl.sheet_names):
                                actual_sheet_name = xl.sheet_names[current_sheet_name]
                            else:
                                raise ValueError(
                                    f"Sheet index {current_sheet_name} out of range for {input_path.name}"
                                )
                            xl.close()
                        except Exception as e_sheetname:
                            log.warning(
                                f"Could not determine sheet name from index {current_sheet_name} for {input_path.name}: {e_sheetname}. Using index as identifier."
                            )
                            actual_sheet_name = f"sheet_{current_sheet_name}"

                except FileNotFoundError:
                    raise  # Already checked, but include for safety
                except ValueError as e:  # Handles sheet not found, etc.
                    raise ValueError(
                        f"Error reading Excel file {input_path.name}: {e}"
                    ) from e
                except Exception as e:  # Catch other pandas/openpyxl errors
                    raise RuntimeError(
                        f"Failed to read Excel file {input_path.name} (sheet: {current_sheet_name}): {e}"
                    ) from e

                if df.empty:
                    log.warning(
                        f"Sheet '{current_sheet_name}' in {input_path.name} is empty or resulted in an empty DataFrame after applying header/skiprows. Skipping."
                    )
                    # Add source entry even if no table created
                    db.add_source(
                        file_name=input_path.name,
                        file_type="xlsx",
                        description=current_description,
                    )
                    continue

                # --- Process Columns ---
                original_headers = list(df.columns)
                columns_to_keep = []
                final_column_names = []  # Sanitized names for the final table
                sdif_columns = {}  # For SDIFDatabase.create_table
                col_name_counts = {}  # To handle duplicate sanitized names

                for original_header in original_headers:
                    if original_header in current_excluded_names:
                        continue  # Skip excluded column

                    columns_to_keep.append(original_header)
                    sanitized_base_name = self._sanitize_name(
                        str(original_header), f"column_{len(sdif_columns)}"
                    )

                    # Handle duplicate sanitized names
                    count = col_name_counts.get(sanitized_base_name, 0) + 1
                    col_name_counts[sanitized_base_name] = count
                    final_col_name = sanitized_base_name
                    if count > 1:
                        final_col_name = f"{sanitized_base_name}_{count - 1}"

                    final_column_names.append(final_col_name)

                    # Prepare column definition for SDIF
                    dtype = df[original_header].dtype
                    sqlite_type = self._map_pandas_dtype_to_sqlite(dtype)
                    sdif_columns[final_col_name] = {
                        "type": sqlite_type,
                        "description": f"Column from Excel sheet '{actual_sheet_name}', header: '{original_header}'",
                        # Add other potential metadata if needed (e.g., original_format for dates handled during prep)
                    }

                if not columns_to_keep:
                    log.warning(
                        f"No columns remaining for sheet '{actual_sheet_name}' in {input_path.name} after exclusions. Skipping table creation."
                    )
                    db.add_source(
                        file_name=input_path.name,
                        file_type="xlsx",
                        description=current_description,
                    )
                    continue

                # Select and rename columns in DataFrame
                df = df[columns_to_keep]
                df.columns = final_column_names

                # --- Determine Table Name ---
                table_base_name: str
                if isinstance(current_input_table_name, str):
                    table_base_name = self._sanitize_name(
                        current_input_table_name, f"table_{i}"
                    )
                else:  # Derive from sheet or filename
                    # Prefer sheet name if available and usable
                    if isinstance(actual_sheet_name, str) and actual_sheet_name:
                        table_base_name = self._sanitize_name(
                            actual_sheet_name, f"table_{i}"
                        )
                    else:  # Fallback to filename stem
                        table_base_name = self._sanitize_name(
                            input_path.stem, f"table_{i}"
                        )

                # Handle duplicate base names across files/sheets
                final_table_name = table_base_name
                count = processed_table_basenames.get(table_base_name, 0) + 1
                processed_table_basenames[table_base_name] = count
                if count > 1:
                    # If a single table name was provided for multiple files OR
                    # if derived names collide
                    is_single_name_multi_file = (
                        isinstance(self.table_names, str) and num_inputs > 1
                    )
                    if is_single_name_multi_file or current_input_table_name is None:
                        final_table_name = f"{table_base_name}_{count - 1}"
                    # Else: User provided a list with duplicates, let create_table handle potential error later
                    # or maybe raise error here? Let's append suffix for safety.
                    else:
                        log.warning(
                            f"Duplicate table name '{table_base_name}' encountered. Appending suffix '_{count - 1}'."
                        )
                        final_table_name = f"{table_base_name}_{count - 1}"

                # --- SDIF Database Operations ---
                source_id = db.add_source(
                    file_name=input_path.name,
                    file_type="xlsx",
                    description=current_description,
                )

                table_desc = f"Data loaded from Excel file: {input_path.name}, sheet: '{actual_sheet_name}'."
                try:
                    db.create_table(
                        table_name=final_table_name,
                        columns=sdif_columns,
                        source_id=source_id,
                        description=table_desc,
                        original_identifier=str(
                            actual_sheet_name
                        ),  # Store sheet name/index
                    )
                except (ValueError, sqlite3.Error) as e:
                    # Re-raise with more context
                    raise RuntimeError(
                        f"Failed to create table '{final_table_name}' for {input_path.name}: {e}"
                    ) from e

                # --- Prepare and Insert Data ---
                try:
                    # Convert DataFrame to list of dicts, applying type conversions for SQLite
                    data_to_insert = []
                    for record in df.to_dict("records"):
                        prepared_record = {
                            col: self._prepare_value_for_sqlite(val)
                            for col, val in record.items()
                        }
                        data_to_insert.append(prepared_record)

                    if data_to_insert:
                        db.insert_data(table_name=final_table_name, data=data_to_insert)

                except Exception as e:
                    raise RuntimeError(
                        f"Failed to prepare or insert data into table '{final_table_name}' from {input_path.name}: {e}"
                    ) from e

        return output_path
