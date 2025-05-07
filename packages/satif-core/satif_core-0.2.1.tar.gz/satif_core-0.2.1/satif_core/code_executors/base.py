from abc import ABC, abstractmethod
from typing import Any, Dict

from satif_core.sdif_db import SDIFDatabase
from satif_core.types import Datasource


class CodeExecutor(ABC):
    """Abstract base class for code executors."""

    @abstractmethod
    def execute(
        self,
        code: str,
        db: SDIFDatabase,
        datasource: Datasource,
        extra_context: Dict[str, Any],
    ) -> None:
        """
        Execute the provided transformation code within a given context.

        Args:
            code: The Python code string to execute.
            db: The SDIFDatabase instance to operate on.
            input_files: List of paths to the input files accessible to the code.
            extra_context: Additional variables to inject into the code's execution scope.

        Raises:
            CodeExecutionError: If there's an error during code execution.
        """
        pass
