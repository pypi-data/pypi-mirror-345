import csv
import decimal
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from typing import Counter as TypingCounter

from satif_core.comparators.base import Comparator

log = logging.getLogger(__name__)

# Helper type hint remains the same
CsvData = Tuple[
    Optional[List[str]],
    Optional[TypingCounter[Tuple[Any, ...]]],
    Optional[str],  # Allow Any for mixed types (str, float)
]


class CsvComparator(Comparator):
    """
    Compares two CSV files for equivalence based on specified criteria.

    Provides a detailed report on differences found in headers and row content.
    Supports options like ignoring row order, header case sensitivity, etc.
    """

    def _read_data(
        self,
        file_path: Union[str, Path],
        delimiter: Optional[str] = None,
        strip_whitespace: bool = True,
        encoding: str = "utf-8",
        decimal_places: Optional[int] = None,  # Add decimal_places parameter
    ) -> CsvData:
        """Helper to read CSV header and row data into a Counter."""
        file_path = Path(file_path)
        header: Optional[List[str]] = None
        row_counts: TypingCounter[Tuple[Any, ...]] = (
            Counter()
        )  # Allow Any type in tuple
        actual_delimiter = delimiter

        try:
            with open(file_path, newline="", encoding=encoding, errors="replace") as f:
                if actual_delimiter is None:
                    try:
                        sample_lines = [line for _, line in zip(range(10), f)]
                        sample = "".join(sample_lines)
                        if not sample:
                            log.debug(
                                f"File {file_path} appears empty during sniffing."
                            )
                            return None, Counter(), None
                        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                        actual_delimiter = dialect.delimiter
                        log.debug(
                            f"Detected delimiter '{actual_delimiter}' for {file_path}"
                        )
                        f.seek(0)
                    except (csv.Error, Exception) as sniff_err:
                        log.warning(
                            f"Could not sniff delimiter for {file_path}, defaulting to ','. Error: {sniff_err}"
                        )
                        actual_delimiter = ","
                        f.seek(0)

                reader = csv.reader(f, delimiter=actual_delimiter)
                try:
                    raw_header = next(reader)
                    header = [h.strip() if strip_whitespace else h for h in raw_header]
                    num_columns = len(header)

                    for i, row in enumerate(reader):
                        if len(row) != num_columns:
                            log.warning(
                                f"Row {i + 2} in {file_path} has {len(row)} columns, expected {num_columns}. Adapting row."
                            )
                            if len(row) > num_columns:
                                row = row[:num_columns]
                            else:
                                row.extend([""] * (num_columns - len(row)))

                        processed_row_values = []
                        for cell in row:
                            value: Any = cell.strip() if strip_whitespace else cell
                            if decimal_places is not None:
                                try:
                                    # Use Decimal for precise rounding
                                    d_value = decimal.Decimal(value)
                                    # Round to specified decimal places
                                    quantizer = decimal.Decimal(
                                        "1e-" + str(decimal_places)
                                    )
                                    value = d_value.quantize(
                                        quantizer, rounding=decimal.ROUND_HALF_UP
                                    )
                                    # Convert back to float for storage if needed, or keep as Decimal
                                    # Keeping as Decimal might be more precise but requires consumers to handle it
                                    # Let's convert back to float for broader compatibility, though precision issues might reappear
                                    value = float(value)
                                except (decimal.InvalidOperation, ValueError):
                                    # Keep as string if conversion fails
                                    pass
                            processed_row_values.append(value)

                        processed_row = tuple(processed_row_values)
                        row_counts[processed_row] += 1

                except StopIteration:
                    log.debug(f"File {file_path} is empty or header-only.")
                    return header, Counter(), None  # Return header if found, else None
                except Exception as read_err:
                    log.error(
                        f"Error reading CSV content from {file_path} after header: {read_err}"
                    )
                    return header, None, f"Error reading content: {read_err}"

            return header, row_counts, None

        except FileNotFoundError:
            log.error(f"File not found: {file_path}")
            return None, None, "File not found"
        except Exception as e:
            log.error(f"Failed to open or process file {file_path}: {e}")
            return None, None, f"Error opening/processing file: {e}"

    def compare(
        self, file_path1: Union[str, Path], file_path2: Union[str, Path], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Compares two CSV files using specified options.

        Kwargs Options:
            ignore_row_order (bool): Compare row content regardless of order (default: True).
            check_header_order (bool): Require header columns in the same order (default: True).
            check_header_case (bool): Ignore case when comparing header names (default: False).
            strip_whitespace (bool): Strip leading/trailing whitespace from headers/cells (default: True).
            delimiter1 (Optional[str]): Delimiter for file 1 (default: auto-detect).
            delimiter2 (Optional[str]): Delimiter for file 2 (default: auto-detect).
            encoding (str): Text encoding for reading files (default: 'utf-8').
            decimal_places (Optional[int]): Number of decimal places to consider for float comparison (default: 2 - 0.01 precision).
            max_examples (int): Max number of differing row examples (default: 5).
        """
        # --- Extract parameters with defaults ---
        file_path1 = Path(file_path1)
        file_path2 = Path(file_path2)
        ignore_row_order: bool = kwargs.get("ignore_row_order", True)
        check_header_order: bool = kwargs.get("check_header_order", True)
        check_header_case: bool = kwargs.get("check_header_case", False)
        strip_whitespace: bool = kwargs.get("strip_whitespace", True)
        delimiter1: Optional[str] = kwargs.get("delimiter1", None)
        delimiter2: Optional[str] = kwargs.get("delimiter2", None)
        encoding: str = kwargs.get("encoding", "utf-8")
        max_examples: int = kwargs.get("max_examples", 5)
        decimal_places: Optional[int] = kwargs.get("decimal_places", 2)

        # --- Initialize results structure ---
        results: Dict[str, Any] = {
            "files": {"file1": str(file_path1), "file2": str(file_path2)},
            "comparison_params": {  # Store actual used parameters
                "ignore_row_order": ignore_row_order,
                "check_header_order": check_header_order,
                "check_header_case": check_header_case,
                "strip_whitespace": strip_whitespace,
                "delimiter1_used": delimiter1,  # Store potentially provided delimiter
                "delimiter2_used": delimiter2,  # Store potentially provided delimiter
                "encoding": encoding,
                "decimal_places": decimal_places,  # Add to params
                "max_examples": max_examples,
            },
            "are_equivalent": True,  # Assume true initially
            "summary": [],
            "details": {
                "errors": [],
                "header_comparison": {"result": "Not compared", "diff": []},
                "row_comparison": {"result": "Comparing..."},
            },
        }

        # --- Read Data using the helper method ---
        header1, rows1_counter, error1 = self._read_data(
            file_path1,
            delimiter1,
            strip_whitespace,
            encoding,
            decimal_places,  # Pass decimal_places
        )
        header2, rows2_counter, error2 = self._read_data(
            file_path2,
            delimiter2,
            strip_whitespace,
            encoding,
            decimal_places,  # Pass decimal_places
        )

        # Update used delimiters if they were auto-detected (optional, for info)
        # Note: _read_data doesn't return the detected delimiter currently, could be added if needed.
        # results["comparison_params"]["delimiter1_used"] = detected_delimiter1 or delimiter1
        # results["comparison_params"]["delimiter2_used"] = detected_delimiter2 or delimiter2

        if error1:
            results["details"]["errors"].append(f"File 1 ({file_path1.name}): {error1}")
            results["are_equivalent"] = False
        if error2:
            results["details"]["errors"].append(f"File 2 ({file_path2.name}): {error2}")
            results["are_equivalent"] = False

        if error1 or error2 or rows1_counter is None or rows2_counter is None:
            results["summary"].append(
                "Comparison aborted due to errors reading file(s)."
            )
            # Ensure row comparison details reflect the error state
            results["details"]["row_comparison"] = {
                "result": "Not compared (error reading files)",
                "row_count1": sum(rows1_counter.values()) if rows1_counter else -1,
                "row_count2": sum(rows2_counter.values()) if rows2_counter else -1,
            }
            return results

        # --- Compare Headers (Logic is identical to previous function) ---
        # ... (copy the exact header comparison logic here) ...
        header_diffs = []
        header_result = "Identical"
        if header1 is None and header2 is None:
            header_result = "Both files have no header (or are empty)."
        elif header1 is None:
            header_result = "Different structure"
            header_diffs.append(f"File 1 has no header, File 2 header: {header2}")
            results["are_equivalent"] = False
        elif header2 is None:
            header_result = "Different structure"
            header_diffs.append(f"File 2 has no header, File 1 header: {header1}")
            results["are_equivalent"] = False
        else:
            h1_compare = header1 if check_header_case else [h.lower() for h in header1]
            h2_compare = header2 if check_header_case else [h.lower() for h in header2]

            if len(h1_compare) != len(h2_compare):
                header_result = "Different column count"
                header_diffs.append(
                    f"File 1 has {len(header1)} columns, File 2 has {len(header2)} columns."
                )
                header_diffs.append(f"File 1 Header: {header1}")
                header_diffs.append(f"File 2 Header: {header2}")
                results["are_equivalent"] = False
            elif check_header_order:
                if h1_compare != h2_compare:
                    header_result = "Different names or order"
                    results["are_equivalent"] = False
                    for i, (h1, h2) in enumerate(zip(h1_compare, h2_compare)):
                        if h1 != h2:
                            orig_h1 = header1[i]
                            orig_h2 = header2[i]
                            case_note = (
                                ""
                                if check_header_case
                                or orig_h1.lower() != orig_h2.lower()
                                else " (differs only by case)"
                            )
                            header_diffs.append(
                                f"Column {i + 1}: File 1 '{orig_h1}' != File 2 '{orig_h2}'{case_note}"
                            )
                elif not check_header_case and header1 != header2:
                    header_result = "Identical names/order (differs only by case)"
                    for i, (h1, h2) in enumerate(zip(header1, header2)):
                        if h1 != h2:
                            header_diffs.append(
                                f"Column {i + 1} case difference: File 1 '{h1}', File 2 '{h2}'"
                            )
            else:  # Ignore order
                if set(h1_compare) != set(h2_compare):
                    header_result = "Different names"
                    results["are_equivalent"] = False
                    only_h1 = set(h1_compare) - set(h2_compare)
                    only_h2 = set(h2_compare) - set(h1_compare)
                    if only_h1:
                        header_diffs.append(f"Headers only in File 1: {list(only_h1)}")
                    if only_h2:
                        header_diffs.append(f"Headers only in File 2: {list(only_h2)}")
                elif h1_compare != h2_compare:
                    header_result = "Identical names (different order)"
                    header_diffs.append(f"File 1 Header Order: {header1}")
                    header_diffs.append(f"File 2 Header Order: {header2}")

        results["details"]["header_comparison"]["result"] = header_result
        results["details"]["header_comparison"]["diff"] = header_diffs
        if header_result not in [
            "Identical",
            "Identical names/order (differs only by case)",
            "Identical names (different order)",
            "Both files have no header (or are empty).",
        ]:
            results["summary"].append(f"Headers differ: {header_result}.")
        elif header_result != "Identical":
            results["summary"].append(
                f"Headers are equivalent but differ slightly: {header_result}."
            )
        else:
            results["summary"].append("Headers are identical.")

        # --- Compare Rows (Logic is identical to previous function) ---
        # ... (copy the exact row comparison logic here) ...
        row_count1 = sum(rows1_counter.values())
        row_count2 = sum(rows2_counter.values())
        results["details"]["row_comparison"] = {
            "result": "Comparing...",
            "row_count1": row_count1,
            "row_count2": row_count2,
            "unique_rows1": [],
            "unique_rows2": [],
            "count_diffs": [],
        }

        can_compare_rows = (
            header1 is not None and header2 is not None and len(header1) == len(header2)
        )

        if can_compare_rows:
            # Initialize row comparison details structure here
            row_comp_details = results["details"]["row_comparison"]  # Shortcut

            if ignore_row_order:
                precision_text = (
                    f" (within {decimal_places} decimal places)"
                    if decimal_places is not None
                    else ""
                )
                row_comp_details["result"] = (
                    f"Comparing content (order ignored){precision_text}..."
                )

                if rows1_counter == rows2_counter:
                    row_comp_details["result"] = f"Identical content{precision_text}"
                    results["summary"].append(
                        f"Row content is identical{precision_text} ({row_count1} rows)."
                    )
                else:
                    results["are_equivalent"] = False
                    row_comp_details["result"] = f"Different content{precision_text}"
                    results["summary"].append(f"Row content differs{precision_text}.")

                    unique_keys1 = list((rows1_counter - rows2_counter).keys())
                    unique_keys2 = list((rows2_counter - rows1_counter).keys())

                    row_comp_details["unique_rows1"] = [
                        list(row) for row in unique_keys1[:max_examples]
                    ]  # Convert tuple back to list for JSON
                    if len(unique_keys1) > 0:
                        row_comp_details["result"] += " (unique rows found)"
                        results["summary"].append(
                            f"Found {len(unique_keys1)} unique row(s) in {file_path1.name}."
                        )

                    row_comp_details["unique_rows2"] = [
                        list(row) for row in unique_keys2[:max_examples]
                    ]  # Convert tuple back to list for JSON
                    if len(unique_keys2) > 0:
                        row_comp_details["result"] += " (unique rows found)"
                        results["summary"].append(
                            f"Found {len(unique_keys2)} unique row(s) in {file_path2.name}."
                        )

                    count_diffs = []
                    keys_to_check = (
                        rows1_counter.keys()
                        if len(rows1_counter) < len(rows2_counter)
                        else rows2_counter.keys()
                    )
                    for key in keys_to_check:
                        if (
                            key in rows1_counter
                            and key in rows2_counter
                            and rows1_counter[key] != rows2_counter[key]
                        ):
                            count_diffs.append(
                                {
                                    "row": list(key),
                                    "count1": rows1_counter[key],
                                    "count2": rows2_counter[key],
                                }
                            )  # Convert tuple back to list

                    row_comp_details["count_diffs"] = count_diffs[:max_examples]
                    if len(count_diffs) > 0:
                        row_comp_details["result"] += " (count differences found)"
                        results["summary"].append(
                            f"Found {len(count_diffs)} row(s) with different occurrence counts{precision_text}."
                        )

                    if row_count1 != row_count2:
                        results["summary"].append(
                            f"Total row counts differ: {file_path1.name} has {row_count1}, {file_path2.name} has {row_count2}."
                        )

            else:  # Compare row order
                row_comp_details["result"] = "Comparing content (order matters)..."
                if row_count1 != row_count2:
                    results["are_equivalent"] = False
                    row_comp_details["result"] = "Different row counts"
                    results["summary"].append(
                        f"Row counts differ (order matters): File 1 has {row_count1}, File 2 has {row_count2}."
                    )
                else:
                    # Placeholder - requires reading into lists
                    row_comp_details["result"] = (
                        "Ordered comparison not fully implemented in V1 (counts match)"
                    )
                    # Need to check if precision text should be added here too?
                    # Let's assume ordered comparison would also need precision handling when implemented.
                    precision_text = (
                        f" (within {decimal_places} decimal places)"
                        if decimal_places is not None
                        else ""
                    )
                    results["summary"].append(
                        f"Files have the same number of rows{precision_text}, but detailed ordered comparison is not fully implemented."
                    )

        # --- Final Summary ---
        if results["are_equivalent"]:
            results["summary"].insert(
                0, "Files are considered equivalent based on the specified parameters."
            )
        else:
            results["summary"].insert(
                0, "Files are considered different based on the specified parameters."
            )

        return results
