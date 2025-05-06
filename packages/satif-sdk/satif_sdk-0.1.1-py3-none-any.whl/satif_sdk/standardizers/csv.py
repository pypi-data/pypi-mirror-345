import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from charset_normalizer import detect
from satif_core import SDIFDatabase, Standardizer
from satif_core.types import Datasource, SDIFPath

# Constants for type inference
SAMPLE_SIZE = 100
# Constants for auto-detection
ENCODING_SAMPLE_SIZE = 1024 * 10  # Bytes for encoding detection
DELIMITER_SAMPLE_SIZE = 1024 * 2  # Bytes for delimiter detection


# TODO:
# - Remove header auto-detection
# - Raise error if auto-delimiter could not find a delimiter
# - Raise error if auto-encoding could not detect an encoding confidently
# - Skip rows could take either an int or a list of ints
# - rename "excluded_column_indexes" to "skip_columns" and handle both int and list of ints


class CSVStandardizer(Standardizer):
    """
    Standardizer for one or multiple CSV files into a single SDIF database.

    Transforms CSV data into the SDIF format, handling single or multiple files.
    Default CSV parsing options (delimiter, encoding, header, skip_rows,
    excluded_column_indexes) are set during initialization. These defaults can
    be overridden on a per-file basis when calling the `standardize` method.
    Includes basic type inference for columns (INTEGER, REAL, TEXT).

    Attributes:
        default_delimiter (Optional[str]): Default CSV delimiter character. If None, attempts auto-detection.
        default_encoding (Optional[str]): Default file encoding. If None, attempts auto-detection.
        default_has_header (bool): Default assumption whether CSV files have a header row.
        default_skip_rows (int): Default number of rows to skip at the beginning of the file.
        default_excluded_column_indexes (Set[int]): Default 0-based indexes of columns to exclude.
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
        skip_rows: int = 0,
        excluded_column_indexes: Optional[List[int]] = None,
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
            skip_rows: Default number of rows to skip at the beginning of the file.
            excluded_column_indexes: Default 0-based indexes of columns to exclude.
                                     Negative indexes are not supported here.
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
                          'skip_rows', 'excluded_column_indexes'. These override the defaults set above.

        """
        if skip_rows < 0:
            raise ValueError("skip_rows cannot be negative.")

        # Default settings (fallbacks)
        self.default_delimiter = delimiter
        self.default_encoding = encoding
        self.default_has_header = has_header
        self.default_skip_rows = skip_rows
        self.default_excluded_column_indexes = set(excluded_column_indexes or [])

        # Task-specific configurations
        self.descriptions = descriptions
        self.table_names = table_names
        self.file_configs = file_configs
        # Store other defaults if needed

    def _sanitize_name(self, name: str, prefix: str = "item") -> str:
        """Clean up a string to be a safe SQL identifier."""
        name = name.strip().lower().replace(" ", "_").replace("-", "_")
        # Ensure it starts with a letter or underscore if not empty
        safe_name = "".join(c for c in name if c.isalnum() or c == "_")
        if safe_name and not (safe_name[0].isalpha() or safe_name[0] == "_"):
            safe_name = f"_{safe_name}"
        return safe_name or prefix  # Return prefix if name becomes empty

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
        """Detect file encoding using charset-normalizer."""
        try:
            with open(file_path, "rb") as fb:
                data = fb.read(sample_size)
                if not data:
                    return "utf-8"  # Default for empty file
                best_guess: Optional[dict] = detect(data)
                if best_guess and best_guess.get("encoding"):
                    return best_guess["encoding"]
                else:
                    print(
                        f"Warning: Encoding detection failed for {file_path.name}. Falling back to utf-8."
                    )
                    return "utf-8"  # Fallback
        except Exception as e:
            print(
                f"Warning: Error during encoding detection for {file_path.name}: {e}. Falling back to utf-8."
            )
            return "utf-8"

    def _detect_delimiter(self, sample_text: str) -> str:
        """Detect CSV delimiter using csv.Sniffer."""
        try:
            # Sniffer needs more than one line usually, handle potential single-line samples
            if "\n" not in sample_text and "\r" not in sample_text:
                # If no newline, try common delimiters directly on the single line
                for delim in [",", ";", "\\t", "|"]:
                    if delim in sample_text:
                        return delim.replace("\\t", "\t")  # Handle tab
                return ","  # Fallback if no common delimiter found

            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample_text)
            return dialect.delimiter
        except csv.Error as e:
            print(f"Warning: Delimiter sniffing failed: {e}. Falling back to ','.")
            # Basic fallback logic if sniffing fails
            if ";" in sample_text:
                return ";"
            if "\t" in sample_text:
                return "\t"
            if "|" in sample_text:
                return "|"
            return ","  # Default fallback
        except Exception as e:
            print(
                f"Warning: Error during delimiter detection: {e}. Falling back to ','."
            )
            return ","

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

                # 1. Encoding Detection/Resolution
                initial_encoding = current_config.get("encoding", self.default_encoding)
                final_encoding: str
                if initial_encoding is None:
                    final_encoding = self._detect_encoding(input_path)
                    print(
                        f"Info: Auto-detected encoding for {input_path.name}: {final_encoding}"
                    )
                else:
                    final_encoding = initial_encoding

                # 2. Delimiter Detection/Resolution (needs a sample with correct encoding)
                initial_delimiter = current_config.get(
                    "delimiter", self.default_delimiter
                )
                final_delimiter: str
                if initial_delimiter is None:
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
                                f"Warning: File {input_path.name} is empty or very small, defaulting delimiter to ','."
                            )
                    except UnicodeDecodeError as e:
                        raise OSError(
                            f"Encoding error reading sample for delimiter detection in {input_path.name} with detected/specified encoding '{final_encoding}': {e}. Try specifying encoding manually."
                        ) from e
                    except Exception as e:
                        print(
                            f"Warning: Error reading sample for delimiter detection in {input_path.name}: {e}. Falling back to ','."
                        )
                        final_delimiter = ","
                else:
                    final_delimiter = initial_delimiter

                # --- Apply other settings ---
                current_has_header = current_config.get(
                    "has_header", self.default_has_header
                )
                user_skip_rows = current_config.get("skip_rows", self.default_skip_rows)
                current_excluded_indexes = set(
                    current_config.get(
                        "excluded_column_indexes", self.default_excluded_column_indexes
                    )
                )
                current_description = processed_descriptions[i]
                current_table_name = final_table_names[i]

                if user_skip_rows < 0:
                    raise ValueError(
                        f"Configured skip_rows cannot be negative (file: {input_path.name})."
                    )

                # --- Calculate Total Rows to Skip (User + Auto Blank) ---
                # (Skip logic moved inside the 'with open' block)
                post_header_pos = 0  # Initialize position after header/first row

                # --- Initialize variables for this file's processing ---
                raw_headers: List[str] = []  # Store original headers before exclusion
                data: List[Dict[str, Any]] = []
                columns: Dict[str, Dict[str, Any]] = {}
                column_keys: List[str] = []  # Final, sanitized, non-excluded keys

                try:
                    # Use determined encoding and delimiter, newline='' is important for csv module
                    with open(input_path, encoding=final_encoding, newline="") as f:
                        # 1. Skip Initial Rows (User + Blank) directly using file object
                        actual_rows_skipped = 0

                        try:
                            # Skip user-defined rows
                            for _ in range(user_skip_rows):
                                f.readline()
                                actual_rows_skipped += 1

                            # Skip blank lines immediately following
                            while True:
                                line = f.readline()
                                if not line:  # EOF reached
                                    break
                                if line.strip():  # First non-blank line
                                    header_line_str = line
                                    post_header_pos = (
                                        f.tell()
                                    )  # Position *after* header line
                                    break
                                else:
                                    actual_rows_skipped += 1

                            if actual_rows_skipped > 0:
                                print(
                                    f"Info: Auto-skipped {actual_rows_skipped} leading blank line(s) after initial {user_skip_rows} skips in {input_path.name}."
                                )

                            # Check if file ended during skips
                            if header_line_str is None:
                                print(
                                    f"Warning: Reached end of file while skipping initial {actual_rows_skipped} rows in {input_path.name}."
                                )
                                db.add_source(
                                    file_name=input_path.name,
                                    file_type="csv",
                                    description=current_description,
                                )
                                continue  # Skip processing this file

                        except Exception as e:
                            raise ValueError(
                                f"Error skipping initial rows ({user_skip_rows} specified + blanks) in {input_path.name}: {e}"
                            ) from e

                        # 2. Determine Headers & Columns (including exclusions)
                        try:
                            # Parse the header_line_str using csv.reader to handle quotes/delimiter correctly
                            header_parser = csv.reader(
                                [header_line_str], delimiter=final_delimiter
                            )
                            first_meaningful_row_fields = next(header_parser)

                            if current_has_header:
                                raw_headers = first_meaningful_row_fields
                            else:
                                raw_headers = [
                                    f"column_{j}"
                                    for j in range(len(first_meaningful_row_fields))
                                ]
                                # If no header, the first meaningful row IS data.
                                # We'll reset the file pointer before data reading.

                            # Build columns dict with cleaned names, considering exclusions
                            temp_columns = {}
                            col_name_counts = {}
                            final_raw_headers = []  # Headers corresponding to final columns
                            for header_idx, header in enumerate(raw_headers):
                                if header_idx in current_excluded_indexes:
                                    continue  # Skip excluded column

                                final_raw_headers.append(
                                    header
                                )  # Keep track of used original headers
                                base_col_name = self._sanitize_name(
                                    header, f"column_{header_idx}"
                                )
                                column_name = base_col_name
                                # Handle duplicates
                                count = col_name_counts.get(base_col_name, 0) + 1
                                col_name_counts[base_col_name] = count
                                if count > 1:
                                    column_name = f"{base_col_name}_{count - 1}"

                                column_keys.append(column_name)  # Store the final key
                                temp_columns[column_name] = {
                                    "type": "TEXT",  # Default, will be inferred later
                                    "description": f"Column from CSV header: '{header}'",
                                }
                            columns = temp_columns

                            if not columns:
                                print(
                                    f"Warning: No columns determined for {input_path.name} after exclusions. Creating source entry only."
                                )
                                db.add_source(
                                    file_name=input_path.name,
                                    file_type="csv",
                                    description=current_description,
                                )
                                continue

                        except StopIteration:  # Handle empty file (after skipping rows)
                            print(
                                f"Warning: CSV file {input_path.name} appears to be empty after skipping rows. Creating source entry only."
                            )
                            db.add_source(
                                file_name=input_path.name,
                                file_type="csv",
                                description=current_description,
                            )
                            continue
                        except Exception as e:
                            raise ValueError(
                                f"Error reading CSV header/first row from {input_path.name}: {e}"
                            ) from e

                        # 3. Infer Column Types (Sampling)
                        sample_data_for_inference = []
                        if columns:
                            try:
                                # If no header, this first meaningful row IS data, include it in sample
                                if not current_has_header:
                                    row_dict = {}
                                    col_len = len(raw_headers)
                                    col_idx_map = {
                                        orig_idx: final_idx
                                        for final_idx, orig_idx in enumerate(
                                            k
                                            for k in range(col_len)
                                            if k not in current_excluded_indexes
                                        )
                                    }
                                    # Use the already parsed fields
                                    for j, value in enumerate(
                                        first_meaningful_row_fields
                                    ):
                                        if j in col_idx_map:
                                            final_key = column_keys[col_idx_map[j]]
                                            row_dict[final_key] = value
                                    if len(row_dict) == len(column_keys):
                                        sample_data_for_inference.append(row_dict)

                                # Seek to start of data (after header) and create sampler reader
                                f.seek(post_header_pos)
                                csv_reader_sample = csv.reader(
                                    f, delimiter=final_delimiter
                                )

                                # Read next N rows for sampling
                                sample_count = 0
                                for sample_row in csv_reader_sample:
                                    # Adjust sample count if we already added the first row
                                    if sample_count >= SAMPLE_SIZE - (
                                        1 if not current_has_header else 0
                                    ):
                                        break
                                    row_dict = {}
                                    row_len = len(sample_row)
                                    col_len = len(
                                        raw_headers
                                    )  # Use original count before exclusion
                                    col_idx_map = {
                                        orig_idx: final_idx
                                        for final_idx, orig_idx in enumerate(
                                            i
                                            for i in range(col_len)
                                            if i not in current_excluded_indexes
                                        )
                                    }

                                    for j, value in enumerate(sample_row):
                                        if j in col_idx_map:
                                            final_key = column_keys[col_idx_map[j]]
                                            row_dict[final_key] = value
                                    if len(row_dict) == len(column_keys):  # Basic check
                                        sample_data_for_inference.append(row_dict)

                                # Perform inference
                                inferred_types = self._infer_column_types(
                                    sample_data_for_inference, column_keys
                                )
                                for col_key, inferred_type in inferred_types.items():
                                    if col_key in columns:
                                        columns[col_key]["type"] = inferred_type

                                # Reset reader to AFTER the header/first data row for full read
                                f.seek(post_header_pos)
                                # Re-create reader as iteration state is consumed
                                csv_reader_main = csv.reader(
                                    f, delimiter=final_delimiter
                                )

                                # Calculate row number offset for warnings/logging
                                row_num_offset = actual_rows_skipped + (
                                    1 if current_has_header else 0
                                )
                                col_idx_map = {
                                    orig_idx: final_idx
                                    for final_idx, orig_idx in enumerate(
                                        i
                                        for i in range(len(raw_headers))
                                        if i not in current_excluded_indexes
                                    )
                                }

                                # Process all remaining rows
                                for row_index, row in enumerate(csv_reader_main):
                                    row_len = len(row)
                                    expected_len = len(
                                        raw_headers
                                    )  # Compare against original raw header count

                                    if row_len != expected_len:
                                        print(
                                            f"Warning: Row {row_index + 1 + row_num_offset} in {input_path.name} has {row_len} columns, "
                                            f"expected {expected_len} based on original header/first row count. "
                                            f"{'Extra data ignored.' if row_len > expected_len else 'Missing values treated as NULL.'}"
                                        )

                                    row_dict = {}
                                    for j, value in enumerate(row):
                                        # Map original index j to final column key, if not excluded
                                        if j in col_idx_map:
                                            final_key_index = col_idx_map[j]
                                            final_key = column_keys[final_key_index]
                                            row_dict[final_key] = value
                                    # Ensure all expected columns are present, even if just NULL/None from short rows
                                    # This is handled by SDIFDatabase insertion if keys are missing.
                                    data.append(row_dict)

                            except Exception as e:
                                print(
                                    f"Warning: Type inference failed for {input_path.name}. Defaulting all columns to TEXT. Error: {e}"
                                )
                                # Ensure columns still default to TEXT if inference fails
                                for col_key in columns:
                                    columns[col_key]["type"] = "TEXT"
                                # Attempt to reset reader anyway
                                try:
                                    # Reset to after header even on error
                                    f.seek(post_header_pos)
                                    csv_reader_main = csv.reader(
                                        f, delimiter=final_delimiter
                                    )
                                except Exception as reset_e:
                                    raise OSError(
                                        f"Failed to reset reader for {input_path.name} after type inference error: {reset_e}"
                                    ) from e

                except UnicodeDecodeError as e:
                    raise OSError(
                        f"Encoding error opening or processing file {input_path.name} with encoding '{final_encoding}': {e}. Please verify the detected encoding or specify it manually."
                    ) from e
                except FileNotFoundError:
                    raise
                except Exception as e:
                    raise OSError(
                        f"Error opening or processing file {input_path}: {e}"
                    ) from e

                # --- SDIF Database Operations ---
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

        return output_path
