import csv
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import clevercsv
from charset_normalizer import detect
from satif_core import SDIFDatabase, Standardizer
from satif_core.types import Datasource, SDIFPath

# Constants for type inference
SAMPLE_SIZE = 100
# Constants for auto-detection
ENCODING_SAMPLE_SIZE = 1024 * 12  # Bytes for encoding detection
DELIMITER_SAMPLE_SIZE = 1024 * 16  # Bytes for delimiter detection


SkipRowsConfig = Optional[Union[int, List[int], Set[int]]]
SkipColumnsConfig = Optional[
    Union[int, str, List[Union[int, str]], Set[Union[int, str]]]
]

# TODO: negative indices on skip_rows and skip_columns


class CSVStandardizer(Standardizer):
    """
    Standardizer for one or multiple CSV files into a single SDIF database.

    Transforms CSV data into the SDIF format, handling single or multiple files.
    Default CSV parsing options (delimiter, encoding, header, skip_rows,
    skip_columns) are set during initialization. These defaults can
    be overridden on a per-file basis when calling the `standardize` method.
    Includes basic type inference for columns (INTEGER, REAL, TEXT).

    Attributes:
        default_delimiter (Optional[str]): Default CSV delimiter character. If None, attempts auto-detection.
        default_encoding (Optional[str]): Default file encoding. If None, attempts auto-detection.
        default_has_header (bool): Default assumption whether CSV files have a header row.
        default_skip_rows_config_raw (SkipRowsConfig): Raw validated config for rows to skip.
        default_skip_columns_config_raw (SkipColumnsConfig): Raw validated config for columns to skip (by index or name).
        descriptions (Optional[Union[str, List[Optional[str]]]]): Descriptions for the data sources.
        table_names (Optional[Union[str, List[Optional[str]]]]): Target table names in the SDIF database.
        file_configs (Optional[Union[Dict[str, Any], List[Optional[Dict[str, Any]]]]]): File-specific configuration overrides.
    """

    def __init__(
        self,
        # Default parsing options (can be overridden by file_configs)
        delimiter: Optional[str] = None,  # Default to None for auto-detection
        encoding: Optional[str] = None,  # Default to None for auto-detection
        has_header: bool = True,
        skip_rows: SkipRowsConfig = 0,
        skip_columns: SkipColumnsConfig = None,
        descriptions: Optional[Union[str, List[Optional[str]]]] = None,
        table_names: Optional[Union[str, List[Optional[str]]]] = None,
        file_configs: Optional[
            Union[Dict[str, Any], List[Optional[Dict[str, Any]]]]
        ] = None,
        # llm_enrichment: bool = False, # Keep for future features
        # llm_model: Optional[str] = None, # Keep for future features
    ):
        """
        Initialize the CSV standardizer with default and task-specific configurations.

        Args:
            delimiter: Default CSV delimiter character. If None, attempts auto-detection.
            encoding: Default file encoding. If None, attempts auto-detection using charset-normalizer.
            has_header: Default assumption whether CSV files have a header row.
            skip_rows: Rows to skip. Can be:
                       - An `int`: Skips the first N rows.
                       - A `List[int]` or `Set[int]`: Skips rows by their specific 0-based index.
                       Defaults to 0 (skip no rows). Non-negative indices only.
            skip_columns: Columns to skip. Can be:
                          - An `int` or `str`: Skip a single column by 0-based index or name.
                          - A `List` or `Set` containing `int` or `str`: Skip multiple columns by index or name.
                          Column names are only effective if `has_header=True`. Non-negative indices only.
                          Defaults to None (skip no columns).
            descriptions: A single description for all sources, or a list of
                          descriptions (one per input file expected in standardize).
                          If None, descriptions are omitted. Used for `sdif_sources.source_description`.
            table_names: A single table name (used as a base if multiple files),
                         a list of table names (one per input file expected in standardize), or None.
                         If None, table names are derived from input filenames.
            file_configs: Optional configuration overrides. Can be a single dict
                          applied to all files, or a list of dicts (one per file expected
                          in standardize, use None in list to apply defaults). Keys in the dict
                          can include 'delimiter', 'encoding', 'has_header',
                          'skip_rows', 'skip_columns'. These override the defaults set above.

        """
        # Validate and store raw default configs
        self.default_skip_rows_config_raw = self._validate_skip_rows_input(skip_rows)
        self.default_skip_columns_config_raw = self._validate_skip_columns_input(
            skip_columns
        )

        # Default settings (fallbacks)
        self.default_delimiter = delimiter
        self.default_encoding = encoding
        self.default_has_header = has_header
        self.default_skip_rows = skip_rows
        self.default_skip_columns = skip_columns

        # Task-specific configurations
        self.descriptions = descriptions
        self.table_names = table_names
        self.file_configs = file_configs
        # Store other defaults if needed

    def _validate_skip_rows_input(
        self, config: SkipRowsConfig, file_name: Optional[str] = None
    ) -> SkipRowsConfig:
        """Validate types and values for skip_rows config."""
        error_context = f" (file: {file_name})" if file_name else ""
        if config is None:
            return 0  # Treat None as 0

        if isinstance(config, int):
            if config < 0:
                raise ValueError(
                    f"skip_rows integer value cannot be negative{error_context}."
                )
            return config
        elif isinstance(config, (list, set)):
            validated_set = set()
            for item in config:
                if not isinstance(item, int):
                    raise TypeError(
                        f"skip_rows list/set must contain only integers{error_context}."
                    )
                if item < 0:
                    raise ValueError(
                        f"skip_rows indices in list/set cannot be negative{error_context}."
                    )
                validated_set.add(item)
            # Return as set for consistency internally when indexed
            return validated_set
        else:
            raise TypeError(
                f"skip_rows must be an integer, a list/set of integers, or None{error_context}."
            )

    def _validate_skip_columns_input(
        self, config: SkipColumnsConfig, file_name: Optional[str] = None
    ) -> SkipColumnsConfig:
        """Validate types and values for skip_columns config."""
        error_context = f" (file: {file_name})" if file_name else ""
        if config is None:
            return None

        if isinstance(config, (int, str)):
            if isinstance(config, int) and config < 0:
                raise ValueError(
                    f"skip_columns integer index cannot be negative{error_context}."
                )
            return config  # Return single int or str
        elif isinstance(config, (list, set)):
            validated_items = []
            for item in config:
                if isinstance(item, int):
                    if item < 0:
                        raise ValueError(
                            f"skip_columns indices in list/set cannot be negative{error_context}."
                        )
                    validated_items.append(item)
                elif isinstance(item, str):
                    validated_items.append(item)
                else:
                    raise TypeError(
                        f"skip_columns list/set must contain only integers or strings{error_context}."
                    )
            # Return as list to preserve type mix for later processing
            return validated_items
        else:
            raise TypeError(
                f"skip_columns must be an int, str, list/set of int/str, or None{error_context}."
            )

    def _sanitize_name(self, name: str, prefix: str = "item") -> str:
        """Clean up a string to be a safe SQL identifier."""
        name = name.strip().lower()
        # Replace common problematic characters with underscores
        name = re.sub(r"[^\w\s-]", "", name)  # Keep word chars, whitespace, hyphen
        name = re.sub(
            r"[-\s]+", "_", name
        )  # Replace hyphens/whitespace with underscore
        # Ensure it starts with a letter or underscore if not empty
        safe_name = "".join(c for c in name if c.isalnum() or c == "_")
        if safe_name and not (safe_name[0].isalpha() or safe_name[0] == "_"):
            safe_name = f"_{safe_name}"
        # Ensure it's not a reserved SQL keyword (basic check)
        if safe_name.upper() in {
            "TABLE",
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "FROM",
            "WHERE",
            "GROUP",
            "ORDER",
            "BY",
            "INDEX",
        }:  # Add more if needed
            safe_name = f"{safe_name}_"
        return safe_name or prefix  # Return prefix if name becomes empty

    def _parse_skip_rows_config(
        self,
        skip_rows_config: SkipRowsConfig,  # Already validated raw config
    ) -> Union[int, Set[int]]:
        """Parse validated skip_rows config into int (for initial skip) or Set[int] (for indexed skip)."""
        if (
            skip_rows_config is None
        ):  # Should have been handled by validation, but belt-and-suspenders
            return 0
        if isinstance(skip_rows_config, int):
            return skip_rows_config
        elif isinstance(skip_rows_config, (list, set)):
            # Validation ensures items are non-negative ints
            return set(skip_rows_config)
        else:
            # Should not happen after validation
            raise TypeError(
                "Internal Error: Invalid type for processed skip_rows_config"
            )

    def _parse_skip_columns_config(
        self,
        skip_columns_config: SkipColumnsConfig,  # Already validated raw config
    ) -> Tuple[Set[int], Set[str]]:
        """Parse validated skip_columns config into separate sets for indices and names."""
        skip_indices: Set[int] = set()
        skip_names: Set[str] = set()

        if skip_columns_config is None:
            return skip_indices, skip_names

        if isinstance(skip_columns_config, int):
            skip_indices.add(skip_columns_config)
        elif isinstance(skip_columns_config, str):
            skip_names.add(skip_columns_config)
        elif isinstance(skip_columns_config, (list, set)):
            for item in skip_columns_config:
                if isinstance(item, int):
                    skip_indices.add(item)
                elif isinstance(item, str):
                    skip_names.add(item)
                # Validation should prevent other types
        else:
            # Should not happen after validation
            raise TypeError(
                "Internal Error: Invalid type for processed skip_columns_config"
            )

        return skip_indices, skip_names

    def _resolve_skip_columns_indices(
        self,
        skip_col_indices: Set[int],
        skip_col_names: Set[str],
        raw_headers: List[str],
        has_header: bool,
        file_name: str,  # For error context
    ) -> Set[int]:
        """Resolve column names to indices and combine with specified indices."""
        final_skip_indices = set(skip_col_indices)
        num_raw_columns = len(raw_headers)

        if skip_col_names:
            if not has_header:
                raise ValueError(
                    f"Cannot skip columns by name ('{skip_col_names}') when has_header=False (file: {file_name}). Please provide column indices."
                )
            if not raw_headers:
                # This shouldn't happen if has_header=True and we read a header line, but check defensively
                raise ValueError(
                    f"Cannot resolve column names ('{skip_col_names}') because no header row was found or processed (file: {file_name})."
                )

            header_map = {name: idx for idx, name in enumerate(raw_headers)}
            unresolved_names = set()

            for name in skip_col_names:
                if name in header_map:
                    final_skip_indices.add(header_map[name])
                else:
                    unresolved_names.add(name)

            if unresolved_names:
                # Try case-insensitive match as a fallback
                header_map_lower = {
                    name.lower(): idx for idx, name in enumerate(raw_headers)
                }
                still_unresolved = set()
                resolved_case_insensitive = set()
                for name in unresolved_names:
                    lower_name = name.lower()
                    if lower_name in header_map_lower:
                        idx = header_map_lower[lower_name]
                        final_skip_indices.add(idx)
                        resolved_case_insensitive.add(name)
                        print(
                            f"Warning: Resolved column name '{name}' case-insensitively to '{raw_headers[idx]}' for skipping (file: {file_name})."
                        )
                    else:
                        still_unresolved.add(name)
                if still_unresolved:
                    raise ValueError(
                        f"Could not find column name(s) specified in skip_columns: {still_unresolved} (available headers: {raw_headers}) (file: {file_name})."
                    )

        # Final check: ensure all resolved indices are within bounds
        if any(idx >= num_raw_columns for idx in final_skip_indices):
            invalid_indices = {
                idx for idx in final_skip_indices if idx >= num_raw_columns
            }
            raise ValueError(
                f"Skip column index/indices out of bounds: {invalid_indices}. File has {num_raw_columns} columns (file: {file_name})."
            )

        return final_skip_indices

    def _parse_row(
        self,
        row_fields: List[str],
        col_idx_map: Dict[int, int],  # Map original_idx -> final_idx
        column_keys: List[str],  # Final column keys/names
        expected_raw_len: int,
        file_name: str,
        row_num_for_logging: int,
    ) -> Optional[Dict[str, Any]]:
        """Parses a list of fields into a dictionary based on the column mapping, handling skips and mismatches."""
        row_len = len(row_fields)
        if row_len != expected_raw_len:
            print(
                f"Warning: Row {row_num_for_logging} in {file_name} has {row_len} columns, "
                f"expected {expected_raw_len} based on original header/first row count. "
                f"{'Extra data ignored.' if row_len > expected_raw_len else 'Missing values treated as NULL.'}"
            )
            # Handle exceptionally short rows - perhaps return None if unusable?
            # If row_len == 0 and expected_raw_len > 0: return None # Skip truly empty rows that aren't expected

        row_dict = {}
        valid_data_found = False
        for original_idx, value in enumerate(row_fields):
            # Map original index j to final column key, if not excluded
            if original_idx in col_idx_map:
                final_key_index = col_idx_map[original_idx]
                if final_key_index < len(column_keys):
                    final_key = column_keys[final_key_index]
                    row_dict[final_key] = value
                    if (
                        value is not None and value != ""
                    ):  # Consider row non-empty if any included column has data
                        valid_data_found = True
                # else: error condition - col_idx_map gave out-of-bounds index

        # Only return a dict if it contains some data for the selected columns,
        # or if it exactly matches the number of expected *final* columns (even if all null/empty)
        if valid_data_found or len(row_dict) == len(column_keys):
            # Ensure all expected final keys are present, even if NULL/None (from short rows)
            # This is implicitly handled by inserting dicts into SDIF, missing keys become NULL.
            return row_dict
        else:
            # Row was likely completely empty or only contained data in skipped columns
            return None

    def _infer_column_types(
        self, sample_data: List[Dict[str, str]], column_keys: List[str]
    ) -> Dict[str, str]:
        """Infer SQLite types (INTEGER, REAL, TEXT) from sample data."""
        potential_types: Dict[str, set] = {
            key: {"INTEGER", "REAL", "TEXT"} for key in column_keys
        }

        for row in sample_data:
            for col_key in column_keys:
                value = row.get(col_key)  # Use .get() in case of missing keys in sample
                if (
                    value is None or value == ""
                ):  # Treat empty strings/None as compatible with any type
                    continue

                current_potentials = potential_types[col_key]
                if not current_potentials:  # Already determined as TEXT or error
                    continue

                # Check Integer
                if "INTEGER" in current_potentials:
                    try:
                        int(value)
                    except ValueError:
                        current_potentials.discard("INTEGER")

                # Check Real (Float) - only if Integer check failed or wasn't possible
                if "REAL" in current_potentials and "INTEGER" not in current_potentials:
                    try:
                        float(value)
                    except ValueError:
                        current_potentials.discard("REAL")
                elif "REAL" in current_potentials and "INTEGER" in current_potentials:
                    # If it wasn't an int, check if it's a float
                    try:
                        val_float = float(value)
                        # Avoid classifying '1.0' as REAL if it could be INTEGER
                        if not val_float.is_integer():
                            current_potentials.discard(
                                "INTEGER"
                            )  # It's definitely float-like
                    except ValueError:
                        current_potentials.discard("INTEGER")  # Not int
                        current_potentials.discard("REAL")  # Not float either

                # If nothing left, it must be TEXT (or error)
                if not current_potentials - {"TEXT"}:
                    potential_types[col_key] = {"TEXT"}

        # Determine final types
        final_types = {}
        for col_key, potentials in potential_types.items():
            if "INTEGER" in potentials:
                final_types[col_key] = "INTEGER"
            elif "REAL" in potentials:
                final_types[col_key] = "REAL"
            else:
                final_types[col_key] = "TEXT"  # Default to TEXT

        return final_types

    def _detect_encoding(
        self, file_path: Path, sample_size: int = ENCODING_SAMPLE_SIZE
    ) -> str:
        """Detect file encoding using charset-normalizer.

        Raises:
            ValueError: If encoding cannot be detected.
            OSError: If there's an error reading the file sample.
        """
        try:
            with open(file_path, "rb") as fb:
                data = fb.read(sample_size)
                if not data:
                    return "utf-8"  # Default for empty file
                best_guess: Optional[dict] = detect(data)
                if best_guess and best_guess.get("encoding"):
                    return best_guess["encoding"]
                else:
                    raise ValueError(
                        f"Error during encoding detection for {file_path.name}: No suitable encoding found. Please specify encoding manually."
                    )
        except Exception as e:
            raise RuntimeError(
                f"Error during encoding detection for {file_path.name}: {e}"
            ) from e

    def _detect_delimiter(self, sample_text: str) -> str:
        """Detect CSV delimiter using clevercsv.Sniffer for robustness.

        Raises:
            ValueError: If the delimiter cannot be automatically determined from the sample.
            RuntimeError: If an unexpected error occurs during detection.
        """
        if not sample_text:
            raise ValueError("Cannot detect delimiter from empty sample text.")
        try:
            sniffer = clevercsv.Sniffer()
            dialect = sniffer.sniff(sample_text)
            if dialect and dialect.delimiter:
                return dialect.delimiter
            else:
                # This case might be less likely with clevercsv, but handle it.
                raise ValueError(
                    "CleverCSV could not reliably determine the delimiter. Please specify it manually."
                )
        except clevercsv.Error as e:
            # If clevercsv sniffer fails explicitly
            raise ValueError(
                f"Could not automatically detect CSV delimiter using CleverCSV. Please specify the delimiter manually. Sniffer error: {e}"
            ) from e
        except Exception as e:
            # Catch other potential errors during sniffing
            raise RuntimeError(
                f"An unexpected error occurred during CleverCSV delimiter detection: {e}"
            ) from e

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
        Standardize one or more CSV files into a single SDIF database file,
        using configurations provided during initialization.

        Args:
            datasource: A single path or a list of paths to the input CSV file(s).
            output_sdif: The path for the output SDIF database file.
            overwrite: If True, overwrite the output SDIF file if it exists.
            config: Optional configuration dictionary (from base class, currently unused).
            **kwargs: Additional keyword arguments (from base class, currently unused).


        Returns:
            The path to the created SDIF database file.

        Raises:
            ValueError: If input files are invalid, list arguments stored in the instance
                        have incorrect lengths compared to datasource, skip_rows is negative,
                        or CSV parsing/database errors occur.
            FileNotFoundError: If an input CSV file does not exist.
            IOError: If file opening or reading fails.
            RuntimeError: If database insertion fails.
        """
        output_path = Path(output_path)
        if isinstance(datasource, (str, Path)):
            input_paths = [Path(datasource)]
        else:
            input_paths = [Path(p) for p in datasource]

        num_inputs = len(input_paths)

        # --- Normalize List Arguments ---
        def normalize_list_arg(arg, arg_name, expected_len):
            if isinstance(arg, (str, dict)) or (
                arg_name == "File configs" and isinstance(arg, dict)
            ):  # Single item applies to all
                return [arg] * expected_len
            elif isinstance(arg, list):
                if len(arg) != expected_len:
                    raise ValueError(
                        f"{arg_name} list length ({len(arg)}) must match "
                        f"input files count ({expected_len})."
                    )
                return arg
            else:  # None or other type
                return [None] * expected_len

        processed_descriptions = normalize_list_arg(
            self.descriptions, "Descriptions", num_inputs
        )
        processed_table_names = normalize_list_arg(
            self.table_names, "Table names", num_inputs
        )
        processed_configs = normalize_list_arg(
            self.file_configs, "File configs", num_inputs
        )

        # Derive table names where None or if single name given for multiple files
        final_table_names = []
        is_single_name_multi_file = isinstance(self.table_names, str) and num_inputs > 1
        for i in range(num_inputs):
            name = processed_table_names[i]
            if name is None or is_single_name_multi_file:
                safe_stem = self._sanitize_name(input_paths[i].stem, f"table_{i}")
                final_table_names.append(safe_stem)
            else:
                # Sanitize provided name as well
                final_table_names.append(
                    self._sanitize_name(str(name), f"table_{i}")
                )  # Ensure string

        with SDIFDatabase(output_path, overwrite=overwrite) as db:
            for i, input_path in enumerate(input_paths):
                if not input_path.exists():
                    raise FileNotFoundError(f"Input CSV file not found: {input_path}")
                if not input_path.is_file():
                    raise ValueError(f"Input path is not a file: {input_path}")

                # --- Determine Effective Configuration ---
                current_config = processed_configs[i] or {}

                # Get raw skip configs, falling back to defaults
                effective_skip_rows_raw = self._validate_skip_rows_input(
                    current_config.get("skip_rows", self.default_skip_rows_config_raw),
                    input_path.name,
                )
                effective_skip_columns_raw = self._validate_skip_columns_input(
                    current_config.get(
                        "skip_columns", self.default_skip_columns_config_raw
                    ),
                    input_path.name,
                )

                # Get other configs
                current_encoding = current_config.get("encoding", self.default_encoding)
                current_delimiter = current_config.get(
                    "delimiter", self.default_delimiter
                )
                current_has_header = current_config.get(
                    "has_header", self.default_has_header
                )
                current_description = processed_descriptions[i]
                current_table_name = final_table_names[i]

                # --- Auto-Detect Encoding/Delimiter if needed ---
                final_encoding: str
                if current_encoding is None:
                    final_encoding = self._detect_encoding(input_path)
                    print(
                        f"Info: Auto-detected encoding for {input_path.name}: {final_encoding}"
                    )
                else:
                    final_encoding = current_encoding

                final_delimiter: str
                if current_delimiter is None:
                    try:
                        with open(input_path, encoding=final_encoding) as f_sample:
                            sample_text = f_sample.read(DELIMITER_SAMPLE_SIZE)
                        if sample_text:
                            final_delimiter = self._detect_delimiter(sample_text)
                            print(
                                f"Info: Auto-detected delimiter for {input_path.name}: '{final_delimiter}'"
                            )
                        else:
                            final_delimiter = ","  # Fallback for empty file
                            print(
                                f"Warning: File {input_path.name} is empty or very small, defaulting delimiter to ','"
                            )
                    except UnicodeDecodeError as e:
                        raise OSError(
                            f"Encoding error reading sample for delimiter detection in {input_path.name} with detected/specified encoding '{final_encoding}': {e}. Try specifying encoding manually."
                        ) from e
                    except Exception as e:
                        print(
                            f"Warning: Error reading sample for delimiter detection in {input_path.name}: {e}. Falling back to ','"
                        )
                        final_delimiter = ","
                else:
                    final_delimiter = current_delimiter

                # --- Read CSV Data and Process Skips ---
                try:
                    # Parse the validated raw skip configs into their operational forms
                    skip_rows_mode = self._parse_skip_rows_config(
                        effective_skip_rows_raw
                    )
                    skip_col_indices_initial, skip_col_names = (
                        self._parse_skip_columns_config(effective_skip_columns_raw)
                    )

                    # Choose the correct processing method based on skip_rows_mode
                    if isinstance(skip_rows_mode, int):
                        columns, column_keys, data = self._process_csv_skip_initial(
                            input_path,
                            final_encoding,
                            final_delimiter,
                            skip_rows_mode,  # Pass the integer count
                            skip_col_indices_initial,
                            skip_col_names,
                            current_has_header,
                        )
                    elif isinstance(skip_rows_mode, set):
                        columns, column_keys, data = self._process_csv_skip_indexed(
                            input_path,
                            final_encoding,
                            final_delimiter,
                            skip_rows_mode,  # Pass the set of indices
                            skip_col_indices_initial,
                            skip_col_names,
                            current_has_header,
                        )
                    else:
                        # This case should be prevented by _parse_skip_rows_config
                        raise TypeError(
                            f"Internal Error: Unexpected type for skip_rows_mode: {type(skip_rows_mode)}"
                        )

                except FileNotFoundError:
                    raise  # Re-raise if file not found during processing
                except (ValueError, TypeError, OSError, UnicodeDecodeError) as e:
                    # Catch specific, expected errors from processing
                    raise RuntimeError(
                        f"Error processing CSV file {input_path.name}: {e}"
                    ) from e
                except Exception as e:
                    # Catch unexpected errors during processing
                    raise RuntimeError(
                        f"Unexpected error processing CSV file {input_path.name}: {e}"
                    ) from e

                # --- SDIF Database Operations ---
                if not columns and not data:
                    print(
                        f"Info: No data processed for {input_path.name}. Adding source entry only."
                    )
                    db.add_source(
                        file_name=input_path.name,
                        file_type="csv",
                        description=current_description,
                    )
                    continue  # Move to next file

                source_id = db.add_source(
                    file_name=input_path.name,
                    file_type="csv",
                    description=current_description,
                )

                if columns:
                    table_desc = f"Data loaded from CSV file: {input_path.name}."
                    db.create_table(
                        table_name=current_table_name,
                        columns=columns,
                        source_id=source_id,
                        description=table_desc,
                    )
                    if data:
                        try:
                            db.insert_data(table_name=current_table_name, data=data)
                        except Exception as e:
                            raise RuntimeError(
                                f"Failed to insert data into table '{current_table_name}' from {input_path.name}: {e}"
                            ) from e
                elif data:
                    # This case should ideally not happen if columns aren't determined but data exists
                    print(
                        f"Warning: Data found for {input_path.name}, but no columns were determined. Skipping table creation/insertion."
                    )

        return output_path

    def _setup_columns(
        self,
        raw_headers: List[str],
        skip_col_indices_initial: Set[int],
        skip_col_names: Set[str],
        has_header: bool,
        file_name: str,
    ) -> Tuple[Dict[str, Dict[str, Any]], List[str], Dict[int, int]]:
        """
        Resolves skip columns and builds the initial columns dict, keys list, and index map.
        Returns: (columns, column_keys, col_idx_map)
        """
        # Resolve skip columns now that headers are known
        final_skip_column_indices = self._resolve_skip_columns_indices(
            skip_col_indices_initial, skip_col_names, raw_headers, has_header, file_name
        )

        # Build columns dict, keys, and index map
        columns: Dict[str, Dict[str, Any]] = {}
        column_keys: List[str] = []
        col_idx_map: Dict[int, int] = {}
        col_name_counts: Dict[str, int] = {}
        final_idx = 0
        for original_idx, header in enumerate(raw_headers):
            if original_idx in final_skip_column_indices:
                continue
            base_col_name = self._sanitize_name(header, f"column_{original_idx}")
            column_name = base_col_name
            count = col_name_counts.get(base_col_name, 0) + 1
            col_name_counts[base_col_name] = count
            if count > 1:
                column_name = f"{base_col_name}_{count - 1}"

            column_keys.append(column_name)
            columns[column_name] = {
                "type": "TEXT",  # Default type
                "description": f"Column from CSV header: '{header}'",
            }
            col_idx_map[original_idx] = final_idx
            final_idx += 1

        if not columns:
            print(f"Warning: No columns determined for {file_name} after exclusions.")
            # Return empty structures if no columns are left
            return {}, [], {}

        return columns, column_keys, col_idx_map

    def _perform_type_inference(
        self,
        sample_data: List[Dict[str, str]],
        columns: Dict[str, Dict[str, Any]],  # Will be modified in place
        column_keys: List[str],
        file_name: str,
        context_msg: str,  # e.g., "(initial skip mode)"
    ):
        """Performs type inference on sample data and updates the columns dict."""
        if not sample_data:
            print(
                f"Info: No sample data collected for type inference in {file_name} {context_msg}. Skipping."
            )
            return
        if not columns or not column_keys:
            print(
                f"Warning: Cannot perform type inference in {file_name} {context_msg} because columns/keys were not determined. Skipping."
            )
            return

        try:
            inferred_types = self._infer_column_types(sample_data, column_keys)
            for col_key, inferred_type in inferred_types.items():
                if col_key in columns:
                    columns[col_key]["type"] = inferred_type
                # else: # This shouldn't happen if column_keys match columns
                #     print(f"Warning: Inferred type for unknown column key '{col_key}' in {file_name}")
        except Exception as e:
            print(
                f"Warning: Type inference failed for {file_name} {context_msg}. Defaulting columns to TEXT. Error: {e}"
            )
            # Ensure columns still default to TEXT if inference fails
            for col_key in columns:
                columns[col_key]["type"] = "TEXT"

    def _process_csv_skip_initial(
        self,
        input_path: Path,
        encoding: str,
        delimiter: str,
        initial_skip_count: int,
        skip_col_indices_initial: Set[int],
        skip_col_names: Set[str],
        has_header: bool,
    ) -> Tuple[Dict[str, Dict[str, Any]], List[str], List[Dict[str, Any]]]:
        """Processes CSV assuming skipping the first N rows."""
        file_name = input_path.name
        data: List[Dict[str, Any]] = []
        columns: Dict[str, Dict[str, Any]] = {}
        column_keys: List[str] = []
        raw_headers: List[str] = []
        col_idx_map: Dict[int, int] = {}
        sample_data_for_inference: List[Dict[str, str]] = []

        with open(input_path, encoding=encoding, newline="") as f:
            actual_rows_skipped = 0
            header_line_str: Optional[str] = None
            post_header_pos = 0

            # Skip initial N lines + blank lines
            try:
                for _ in range(initial_skip_count):
                    f.readline()
                    actual_rows_skipped += 1
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.strip():
                        header_line_str = line
                        post_header_pos = f.tell()
                        break
                    else:
                        actual_rows_skipped += 1
                blank_lines_skipped = actual_rows_skipped - initial_skip_count
                if blank_lines_skipped > 0:
                    print(
                        f"Info: Skipped {blank_lines_skipped} leading blank line(s) after initial {initial_skip_count} skips in {file_name}."
                    )

                if header_line_str is None:
                    print(
                        f"Warning: Reached EOF while skipping initial rows in {file_name}."
                    )
                    return {}, [], []  # Return empty if nothing after skips

            except Exception as e:
                raise ValueError(
                    f"Error skipping initial rows in {file_name}: {e}"
                ) from e

            # Process header/first data row
            try:
                header_parser = csv.reader([header_line_str], delimiter=delimiter)
                first_meaningful_row_fields = next(header_parser)
            except StopIteration:
                print(
                    f"Warning: File {file_name} seems empty after skipping initial rows."
                )
                return {}, [], []
            except Exception as e:
                raise ValueError(
                    f"Error parsing first non-skipped row in {file_name}: {e}"
                ) from e

            num_raw_columns = len(first_meaningful_row_fields)
            if has_header:
                raw_headers = first_meaningful_row_fields
            else:
                raw_headers = [f"column_{j}" for j in range(num_raw_columns)]

            # --- Setup Columns ---
            columns, column_keys, col_idx_map = self._setup_columns(
                raw_headers,
                skip_col_indices_initial,
                skip_col_names,
                has_header,
                file_name,
            )

            # Bail out if column setup resulted in no columns
            if not columns:
                return {}, [], []

            # Row offset for logging
            row_num_offset = actual_rows_skipped + (1 if has_header else 0)

            # Type Inference Sampling
            f.seek(post_header_pos)  # Go back to start of data
            csv_reader_sample = csv.reader(f, delimiter=delimiter)
            sample_count = 0
            # Add first data row if no header
            if not has_header:
                parsed_first_row = self._parse_row(
                    first_meaningful_row_fields,
                    col_idx_map,
                    column_keys,
                    num_raw_columns,
                    file_name,
                    row_num_offset,
                )
                if parsed_first_row:
                    sample_data_for_inference.append(parsed_first_row)
                sample_count += 1  # Count this row towards sample size

            for sample_row_fields in csv_reader_sample:
                if sample_count >= SAMPLE_SIZE:
                    break
                parsed_row = self._parse_row(
                    sample_row_fields,
                    col_idx_map,
                    column_keys,
                    num_raw_columns,
                    file_name,
                    row_num_offset + sample_count + (1 if has_header else 0),
                )
                if parsed_row:
                    sample_data_for_inference.append(parsed_row)
                sample_count += 1

            if sample_data_for_inference:
                self._perform_type_inference(
                    sample_data_for_inference,
                    columns,
                    column_keys,
                    file_name,
                    "(initial skip mode)",
                )

            # Read Full Data
            f.seek(post_header_pos)
            csv_reader_main = csv.reader(f, delimiter=delimiter)
            # If no header, first row might have been processed for sample, re-parse or skip?
            # Re-parse is safer and cleaner. _parse_row handles it.
            for row_index, row_fields in enumerate(csv_reader_main):
                current_log_row_num = row_num_offset + row_index + 1
                parsed_row = self._parse_row(
                    row_fields,
                    col_idx_map,
                    column_keys,
                    num_raw_columns,
                    file_name,
                    current_log_row_num,
                )
                if parsed_row:
                    data.append(parsed_row)

        return columns, column_keys, data

    def _process_csv_skip_indexed(
        self,
        input_path: Path,
        encoding: str,
        delimiter: str,
        skip_row_indices: Set[int],
        skip_col_indices_initial: Set[int],
        skip_col_names: Set[str],
        has_header: bool,
    ) -> Tuple[Dict[str, Dict[str, Any]], List[str], List[Dict[str, Any]]]:
        """Processes CSV assuming skipping rows by specific indices."""
        file_name = input_path.name
        data: List[Dict[str, Any]] = []
        columns: Dict[str, Dict[str, Any]] = {}
        column_keys: List[str] = []
        raw_headers: Optional[List[str]] = None
        col_idx_map: Optional[Dict[int, int]] = None
        sample_data_for_inference: List[Dict[str, str]] = []
        columns_determined = False
        header_processed = False  # Track if the designated header row is processed
        num_raw_columns = 0  # Store number of columns from header/first row

        with open(input_path, encoding=encoding, newline="") as f:
            csv_reader_main = csv.reader(f, delimiter=delimiter)

            for row_index, row_fields in enumerate(csv_reader_main):
                if row_index in skip_row_indices:
                    continue  # Skip this row

                current_log_row_num = row_index + 1  # 1-based index for logging

                # --- Determine Columns and Header ---
                if not columns_determined:
                    if (
                        not row_fields
                    ):  # Skip truly empty rows before determining columns
                        print(
                            f"Info: Skipping empty row {current_log_row_num} in {file_name} before header determination."
                        )
                        continue

                    num_raw_columns = len(row_fields)
                    if has_header and not header_processed:
                        raw_headers = row_fields
                        header_processed = True  # Mark header as processed
                    elif not raw_headers:  # First non-skipped, non-empty row and no header expected or found yet
                        raw_headers = [f"column_{j}" for j in range(num_raw_columns)]

                    # Now that raw_headers are potentially set, resolve columns
                    if raw_headers is not None:
                        # --- Setup Columns ---
                        columns, column_keys, col_idx_map = self._setup_columns(
                            raw_headers,
                            skip_col_indices_initial,
                            skip_col_names,
                            has_header,
                            file_name,
                        )
                        columns_determined = True

                        # Bail out if column setup resulted in no columns
                        if not columns:
                            return {}, [], []

                        # If this row *was* the header, skip adding it to data/sample
                        if has_header and header_processed:
                            continue
                        # If it wasn't the header, it's the first data row; potentially use for sample
                        if not has_header:
                            parsed_row = self._parse_row(
                                row_fields,
                                col_idx_map,
                                column_keys,
                                num_raw_columns,
                                file_name,
                                current_log_row_num,
                            )
                            if (
                                parsed_row
                                and len(sample_data_for_inference) < SAMPLE_SIZE
                            ):
                                sample_data_for_inference.append(parsed_row)
                            # Also add to main data
                            if parsed_row:
                                data.append(parsed_row)
                            continue  # Move to next row after processing this first data row

                # --- Process Regular Data Row ---
                # This block executes if columns are determined and the current row wasn't skipped or the header
                if columns_determined and col_idx_map is not None:
                    parsed_row = self._parse_row(
                        row_fields,
                        col_idx_map,
                        column_keys,
                        num_raw_columns,
                        file_name,
                        current_log_row_num,
                    )
                    if parsed_row:
                        # Add to sample if needed
                        if len(sample_data_for_inference) < SAMPLE_SIZE:
                            sample_data_for_inference.append(parsed_row)
                        # Add to main data
                        data.append(parsed_row)

            # --- Type Inference (using sample) ---
            if sample_data_for_inference:
                self._perform_type_inference(
                    sample_data_for_inference,
                    columns,
                    column_keys,
                    file_name,
                    "(indexed skip mode)",
                )
            elif not data and columns:
                print(
                    f"Info: No data rows found or processed for {file_name} after skipping; columns determined but type inference skipped."
                )
            elif not columns:
                # Should have returned earlier if columns failed
                pass

        return columns, column_keys, data
