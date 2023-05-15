"""Base classes of Config object."""
from typing import TYPE_CHECKING, Any, Dict, List

# Imports Processing for mypy type checking only
if TYPE_CHECKING:
    from cliconfig.processing.base import Processing


class Config:
    """Class for configuration.

    Config object contain the config dict and the processing list
    and no methods except ``__init__``, ``__repr__`` and ``__eq__``.
    The Config objects are mutable and not hashable.
    """

    def __init__(
        self, config_dict: Dict[str, Any], process_list: List["Processing"]
    ) -> None:
        self.dict = config_dict
        self.process_list = process_list

    def __repr__(self) -> str:
        """Representation of Config object."""
        process_classes = [process.__class__.__name__ for process in self.process_list]
        return f"Config({self.dict}, {process_classes})"

    def __eq__(self, other: Any) -> bool:
        """Equality operator.

        Two Config objects are equal if their dicts are equal and their
        lists of Processing objects are equal (order doesn't matter).
        """
        if (
            isinstance(other, Config)
            and self.dict == other.dict
            and len(self.process_list) == len(other.process_list)
        ):
            equal = True
            for processing in self.process_list:
                equal = equal and processing in other.process_list
            for processing in other.process_list:
                equal = equal and processing in self.process_list
            return equal
        return False
