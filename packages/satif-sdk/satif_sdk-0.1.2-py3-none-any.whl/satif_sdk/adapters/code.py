import inspect
import json
import logging
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import pandas as pd
from satif_core.adapters.base import Adapter
from satif_core.sdif_db import SDIFDatabase
from satif_core.types import SDIFPath

logger = logging.getLogger(__name__)


class AdapterError(Exception):
    """Custom exception for adapter errors."""

    pass


class CodeAdapter(Adapter):
    """
    Executes custom Python code to adapt data within an SDIF database,
    producing a new, adapted SDIF database file.

    The adaptation logic operates directly on an SDIFDatabase instance.

    The adaptation logic can be provided as:
    - A Python function
    - A string containing Python code
    - A path to a Python script file

    The function should have one of these signatures:
    - def func(db: SDIFDatabase) -> None:
    - def func(db: SDIFDatabase, context: Dict[str, Any]) -> None:
      The function should modify the passed SDIFDatabase instance *in place*.

    Args:
        function: The function, code string, or file path containing the adaptation logic.
        function_name: Name of the function to execute (defaults to "adapt").
        extra_context: Optional dictionary of objects to inject into the code's execution scope
                       and pass to the adaptation function if it accepts a 'context' argument.
        output_suffix: Suffix to add to the input filename for the output adapted file
                       (defaults to "_adapted"). Set to "" to overwrite (not recommended).
    """

    def __init__(
        self,
        function: Union[Callable, str, Path],
        function_name: str = "adapt",
        extra_context: Optional[Dict[str, Any]] = None,
        output_suffix: str = "_adapted",
    ):
        self.adapt_function_obj: Optional[Callable] = None
        self.adapt_code: Optional[str] = None
        self.function_name = function_name
        self.extra_context = extra_context or {}
        self.output_suffix = output_suffix
        self.function = function

        # Internal state
        self._current_output_path: Optional[Path] = None

        self._init_adapt_function()

    def _init_adapt_function(self):
        """Initialize the adaptation function based on the input type."""
        function = self.function

        if callable(function):
            self.adapt_function_obj = function
            self.function_name = function.__name__  # Use actual function name
        elif isinstance(function, str):
            # Treat as code string by default
            self.adapt_code = function
            # function_name remains as provided or default 'adapt'
        elif isinstance(function, Path):
            try:
                with open(function) as f:
                    self.adapt_code = f.read()
                # function_name remains as provided or default 'adapt'
            except Exception as e:
                raise ValueError(
                    f"Failed to read adaptation function from file {function}: {e}"
                ) from e
        else:
            raise TypeError(
                "function must be a callable Python function, a string containing code, or a Path to a Python file"
            )

    def _load_adapt_function(self) -> Callable:
        """Executes the code string and retrieves the target adaptation function."""
        if self.adapt_code is None:
            # This should not happen if _init_adapt_function was called correctly
            raise AdapterError("No adaptation code available to load.")

        # Prepare execution scope with common libraries and extra context
        # Added numpy as 'np'
        execution_globals = {
            "pd": pd,
            "np": __import__("numpy")
            if "numpy" not in globals()
            else globals()["numpy"],  # Ensure numpy is available
            "json": json,
            "Path": Path,
            "sqlite3": sqlite3,
            "datetime": datetime,
            "timedelta": timedelta,
            "SDIFDatabase": SDIFDatabase,  # Allow the code to potentially use the class
            "AdapterError": AdapterError,  # Make exception available to user code
            "logging": logging,
            "__builtins__": __builtins__,
            **self.extra_context,
        }
        execution_locals = {}

        try:
            # TODO: Use the code executor instead of compile()
            compiled_code = compile(self.adapt_code, "<adaptation_string>", "exec")
            exec(compiled_code, execution_globals, execution_locals)
        except Exception as e:
            logger.exception("Error executing adaptation code string:")
            raise AdapterError(f"Error during adaptation code execution: {e}") from e

        # Find the target function within the executed code's scope
        if self.function_name not in execution_locals:
            raise AdapterError(
                f"Function '{self.function_name}' not found after executing the code string."
            )

        adapt_func = execution_locals[self.function_name]
        if not callable(adapt_func):
            raise AdapterError(
                f"'{self.function_name}' defined in the code string is not a callable function."
            )

        # Store the loaded function object for potential reuse
        self.adapt_function_obj = adapt_func
        return adapt_func

    def _get_adapt_function(self) -> Callable:
        """Get the adaptation function, loading it from code if necessary."""
        if self.adapt_function_obj is not None:
            return self.adapt_function_obj

        if self.adapt_code is not None:
            return self._load_adapt_function()

        # If neither object nor code is set, initialization failed
        raise AdapterError("No adaptation function or code available")

    # Updated signature: accepts a path, not an SDIFDatabase instance
    def adapt(self, sdif_database_path: Union[str, Path]) -> SDIFPath:
        """
        Applies the adaptation logic to the input SDIF database file,
        producing a new adapted SDIF file.

        Args:
            sdif_database_path: The path to the input SDIF database file.
                               This file will be copied before modification.

        Returns:
            The path to the newly created adapted SDIF file.

        Raises:
            FileNotFoundError: If the input SDIF file path does not exist.
            AdapterError: If code execution or adaptation logic fails.
            Exception: For other unexpected errors.
        """
        # Use the provided path directly
        input_path = Path(sdif_database_path).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input SDIF file not found: {input_path}")

        # Determine output path
        output_filename = f"{input_path.stem}{self.output_suffix}{input_path.suffix}"
        # Place output next to input by default
        self._current_output_path = (input_path.parent / output_filename).resolve()

        logger.info(
            f"Starting adaptation. Input: {input_path}, Output: {self._current_output_path}"
        )

        # 1. Copy the input database to the output path
        try:
            if self._current_output_path.exists():
                if self.output_suffix == "":
                    logger.warning(
                        f"Overwriting existing file: {self._current_output_path}"
                    )
                    self._current_output_path.unlink()
                else:
                    logger.warning(
                        f"Output file {self._current_output_path} exists, overwriting."
                    )
                    self._current_output_path.unlink()

            shutil.copy2(input_path, self._current_output_path)
            logger.debug(f"Copied {input_path} to {self._current_output_path}")
        except Exception as e:
            raise AdapterError(
                f"Failed to copy input SDIF to output path {self._current_output_path}: {e}"
            ) from e

        # 2. Execute the adaptation code on the copied database
        try:
            # Open the copied database for modification
            # Use 'with' to ensure connection is closed afterwards
            with SDIFDatabase(
                self._current_output_path, read_only=False
            ) as db_to_modify:
                adapt_func = self._get_adapt_function()
                logger.debug(
                    f"Executing adaptation function '{self.function_name}' on {self._current_output_path}"
                )

                # Check function signature to decide how to call it
                sig = inspect.signature(adapt_func)
                param_count = len(sig.parameters)
                params = list(sig.parameters.keys())

                if param_count == 1 and params[0] == "db":
                    result = adapt_func(db=db_to_modify)
                elif param_count >= 2 and params[0] == "db" and params[1] == "context":
                    result = adapt_func(db=db_to_modify, context=self.extra_context)
                else:
                    expected_sigs = [
                        f"def {self.function_name}(db: SDIFDatabase)",
                        f"def {self.function_name}(db: SDIFDatabase, context: Dict[str, Any])",
                    ]
                    raise AdapterError(
                        f"Adaptation function '{self.function_name}' has an invalid signature. "
                        f"Expected one of:\n"
                        + "\n".join(expected_sigs)
                        + f"\nGot: {sig}"
                    )

                if result is not None:
                    logger.warning(
                        f"Adaptation function '{self.function_name}' returned a value ({type(result)}). "
                        "It should modify the SDIFDatabase instance in place and return None."
                    )

            logger.info(
                f"Adaptation function '{self.function_name}' executed successfully."
            )

        except (AdapterError, ValueError, TypeError, sqlite3.Error) as e:
            logger.exception(
                f"Error during execution of adaptation function '{self.function_name}'"
            )
            if self._current_output_path and self._current_output_path.exists():
                try:
                    self._current_output_path.unlink()
                    logger.debug(
                        f"Removed potentially corrupted output file: {self._current_output_path}"
                    )
                except OSError as unlink_err:
                    logger.error(
                        f"Failed to remove corrupted output file {self._current_output_path}: {unlink_err}"
                    )
            raise AdapterError(f"Error during adaptation: {e}") from e
        except Exception as e:
            logger.exception(
                f"Unexpected error during adaptation process for {input_path}"
            )
            if self._current_output_path and self._current_output_path.exists():
                try:
                    self._current_output_path.unlink()
                except OSError:
                    pass
            raise AdapterError(f"Unexpected error during adaptation: {e}") from e

        # 3. Return the path to the adapted database
        final_path = self._current_output_path
        self._current_output_path = None
        if not final_path or not final_path.exists():
            raise AdapterError(
                "Adaptation process completed but output file was not found."
            )

        return final_path
