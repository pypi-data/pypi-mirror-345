from pathlib import Path
from typing import Any, List

from satif_core.comparators.base import Comparator

from .csv import CsvComparator


def get_comparator(file_extension: str, **kwargs: Any) -> Comparator:
    if "csv" in file_extension.lower():
        return CsvComparator(**kwargs)
    # elif "xlsx" in file_extension.lower():
    #     return XlsxComparator() # When implemented
    else:
        raise ValueError(f"No comparator available for extension: {file_extension}")


def compare_output_files(
    generated_output_files: List[Path], target_output_files: List[Path]
) -> dict[str, Any]:
    """
    Compare generated output files with target output files.

    Args:
        generated_output_files: List of paths to generated output files
        target_output_files: List of paths to target output files

    Returns:
        Dictionary containing comparison results and success status
    """
    comparison_results = []
    success = True

    # Check if we have the same number of files
    if len(generated_output_files) != len(target_output_files):
        print(
            f"⚠️ Files count mismatch: {len(generated_output_files)} generated vs {len(target_output_files)} expected"
        )
        success = False

    # Compare each pair of files
    for generated_output_file, target_output_file in zip(
        generated_output_files, target_output_files
    ):
        try:
            comparator = get_comparator(target_output_file.suffix)
            comparison_result = comparator.compare(
                generated_output_file, target_output_file
            )
            comparison_results.append(comparison_result)

            if not comparison_result["are_equivalent"]:
                print(
                    f"❌ Files not equivalent: {generated_output_file} vs {target_output_file}"
                )
                success = False
        except Exception as e:
            print(f"❌ Comparison error: {e}")
            success = False

    return {
        "comparison_results": comparison_results,
        "success": success,
    }


__all__ = ["Comparator", "CsvComparator", "get_comparator", "compare_output_files"]
