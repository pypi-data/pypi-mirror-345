import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from satif_core import CodeExecutor, SDIFDatabase
from satif_core.exceptions import CodeExecutionError
from satif_core.types import Datasource

logger = logging.getLogger(__name__)


class LocalCodeExecutor(CodeExecutor):
    """
    Executes code locally using Python's `exec`.

    **Warning:** This executor is insecure as it runs arbitrary code provided by the user
    directly on the host machine. Use with extreme caution and only in trusted environments.
    """

    def execute(
        self,
        code: str,
        db: SDIFDatabase,
        datasource: Datasource,
        extra_context: Dict[str, Any],
    ) -> None:
        """Executes the code using `exec`."""
        execution_globals = {
            "db": db,
            "datasource": datasource,
            "datetime": datetime,
            "timedelta": timedelta,
            "Path": Path,  # Make Path available
            "__builtins__": __builtins__,  # Provide standard builtins
            **extra_context,
        }
        execution_locals = {}

        logger.warning(
            "Executing user-provided code locally using 'exec'. "
            "This is insecure and should only be used in trusted environments."
        )

        try:
            # Ensure the code runs within the 'with db:' context implicitly
            # The user's code expects to be *inside* the with block.
            # We prepare the context, but the user code interacts with 'db'.
            compiled_code = compile(code, "<string>", "exec")
            exec(compiled_code, execution_globals, execution_locals)
        except Exception as e:
            logger.exception("Error executing user code:")
            raise CodeExecutionError(f"Error during code execution: {e}") from e
