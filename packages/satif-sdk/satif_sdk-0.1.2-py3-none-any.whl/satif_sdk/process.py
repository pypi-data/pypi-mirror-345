from pathlib import Path
from typing import List, Optional

from satif_core.types import Datasource


def process(
    datasource: Datasource,
    *,
    output_files: Optional[List[Path]] = None,
    instructions: Optional[str] = None,
    overwrite: bool = False,
) -> Path: ...


async def aprocess(
    datasource: Datasource,
    *,
    output_files: Optional[List[Path]] = None,
    instructions: Optional[str] = None,
    overwrite: bool = False,
) -> Path: ...
