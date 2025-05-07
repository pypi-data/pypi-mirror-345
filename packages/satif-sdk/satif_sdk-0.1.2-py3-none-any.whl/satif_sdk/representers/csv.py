import csv
import logging
from pathlib import Path
from typing import Any, List, Union

from satif_core.representers.base import Representer

log = logging.getLogger(__name__)


class CsvRepresenter(Representer):
    """Generates representation for CSV files."""

    def represent(
        self, file_path: Union[str, Path], num_rows: int = 10, **kwargs: Any
    ) -> str:
        """
        Generates a string representation of a CSV file by showing
        the header and the first N data rows.

        Kwargs Options:
            encoding (str): File encoding (default: 'utf-8').
            delimiter (Optional[str]): Specify delimiter, otherwise auto-detect (default: None).
        """
        file_path = Path(file_path)

        log.debug(f"Reading CSV representation for: {file_path}")

        encoding = kwargs.get("encoding", "utf-8")
        specified_delimiter = kwargs.get("delimiter", None)
        representation_lines: List[str] = []

        if not file_path.is_file():
            # Although factory might check, double-check here
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            delimiter = specified_delimiter
            # Try to detect dialect if delimiter not specified
            if delimiter is None:
                try:
                    with open(
                        file_path, newline="", encoding=encoding, errors="ignore"
                    ) as f_sniff:
                        sample = "\n".join([line for _, line in zip(range(5), f_sniff)])
                        if sample:
                            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                            delimiter = dialect.delimiter
                            log.debug(
                                f"Detected CSV delimiter: '{delimiter}' for {file_path}"
                            )
                        else:
                            delimiter = ","  # Default for empty file
                except (csv.Error, UnicodeDecodeError, Exception) as sniff_err:
                    log.warning(
                        f"Could not reliably sniff CSV dialect for {file_path}, defaulting to ','. Error: {sniff_err}"
                    )
                    delimiter = ","  # Default on error
            else:
                log.debug(
                    f"Using specified CSV delimiter: '{delimiter}' for {file_path}"
                )

            # Now read using the detected or specified delimiter
            with open(file_path, newline="", encoding=encoding, errors="replace") as f:
                reader = csv.reader(f, delimiter=delimiter)
                try:
                    header = next(reader)
                    representation_lines.append(delimiter.join(header))
                    for i, row in enumerate(reader):
                        if i >= num_rows:
                            break
                        representation_lines.append(delimiter.join(map(str, row)))

                    if (
                        i < num_rows - 1 and i > -1
                    ):  # Check if loop finished early but read some rows
                        log.debug(
                            f"Read {i + 1} data rows from {file_path} (less than requested {num_rows})."
                        )

                except StopIteration:
                    # Handle empty file or header-only file
                    if representation_lines:  # Header was read
                        log.debug(f"CSV file {file_path} has header but no data rows.")
                        representation_lines.append("[No data rows found]")
                    else:  # File was completely empty
                        log.debug(f"CSV file {file_path} appears empty.")
                        return "[CSV file appears empty]"
                except Exception as e:
                    log.error(f"Error reading CSV content from {file_path}: {e}")
                    return f"[Error reading CSV content: {e}]"

        except Exception as e:
            log.error(f"Error opening or processing CSV file {file_path}: {e}")
            return f"[Error opening/processing CSV file {file_path}: {e}]"

        return "\n".join(representation_lines)
