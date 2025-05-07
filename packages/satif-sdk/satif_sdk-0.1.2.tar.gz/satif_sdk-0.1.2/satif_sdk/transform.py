from pathlib import Path
from typing import Any, Dict, Optional, Union

from satif_core import SDIFDatabase, Transformer
from satif_core.types import SDIFPath


def transform(
    sdif: Union[SDIFPath, SDIFDatabase],
    transformer: Transformer,
    *,
    output_path: Optional[Path] = None,
    artifact_dir: Optional[Path] = None,
    overwrite: bool = False,
    zip_archive: bool = False,
) -> Dict[str, Any] | Path:
    if not overwrite and output_path.exists():
        raise FileExistsError(f"Output file {output_path} already exists.")

    transformed_data = transformer.transform(sdif)
    if output_path is None:
        return transformed_data
    else:
        return transformer._export_data(
            data=transformed_data, output_path=output_path, zip_archive=zip_archive
        )
