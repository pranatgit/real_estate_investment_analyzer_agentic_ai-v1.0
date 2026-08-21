"""Abstract base class for the five investment agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """Common contract for all investment agents.

    The assignment requires one public entry point: ``analyze``.
    """

    @abstractmethod
    def analyze(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        """Analyze the supplied property data and return one result dictionary."""
        raise NotImplementedError
