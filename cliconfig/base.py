"""Base classes."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List

# Imports Processing for mypy only
if TYPE_CHECKING:
    from cliconfig.processing.base import Processing


@dataclass
class Config():
    """Class for configuration. It stores the config dict and the processing list."""

    dict: Dict[str, Any]  # noqa: A003
    process_list: List["Processing"]
