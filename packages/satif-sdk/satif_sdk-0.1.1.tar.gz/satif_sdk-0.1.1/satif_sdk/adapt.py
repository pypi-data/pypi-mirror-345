from typing import Any, Dict, Optional, Union

from satif_core import SDIFDatabase
from satif_core.types import SDIFPath


def adapt(
    sdif: Union[SDIFPath, SDIFDatabase],
    *,
    overwrite_output: bool = False,
    config: Optional[Dict[str, Any]] = None,
) -> SDIFPath: ...
