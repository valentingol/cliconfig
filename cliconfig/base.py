"""Base classes of Config object."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Imports Processing for mypy type checking only
if TYPE_CHECKING:
    from cliconfig.processing.base import Processing


class Config:
    """Class for configuration.

    Config object contain the config dict and the processing list
    and no methods except ``__init__``, ``__repr__``, ``__eq__``,
    ``__getattribute__``, ``__setattr__`` and ``__delattr__``.
    The Config objects are mutable and not hashable.

    Parameters
    ----------
    config_dict : Dict[str, Any]
        The config dict.
    process_list : Optional[List[Processing]], optional
        The list of Processing objects. If None, an empty list is used.
        The default is None.
    """

    def __init__(
        self,
        config_dict: Dict[str, Any],
        process_list: Optional[List["Processing"]] = None,
    ) -> None:
        self.dict = config_dict
        self.process_list = process_list if process_list else []

    def __dir__(self) -> List[str]:
        """List of attributes, sub-configurations and parameters."""
        return ["dict", "process_list"] + list(self.dict.keys())

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

    def __getattribute__(self, __name: str) -> Any:
        """Get attribute, sub-configuration or parameter.

        The dict should be nested (unflattened). If it is not the case,
        you can apply :func:`dict_routines.flatten` on ``config.dict``
        to unflatten it.
        """
        if __name in ["dict", "process_list"]:
            return super().__getattribute__(__name)
        if __name not in self.dict:
            keys = ", ".join(self.dict.keys())
            raise AttributeError(  # pylint: disable=raise-missing-from
                f"Config has no attribute '{__name}'. Available keys are: {keys}."
            )
        if isinstance(self.dict[__name], dict):
            # If the attribute is a dict, return a Config object
            # so that we can access the nested keys with multiple dots
            return Config(self.dict[__name], process_list=self.process_list)
        return self.dict[__name]

    def __setattr__(self, __name: str, value: Any) -> None:
        """Set attribute, sub-configuration or parameter.

        The dict should be nested (unflattened). If it is not the case,
        you can apply :func:`dict_routines.flatten` on ``config.dict``
        to unflatten it.
        """
        if __name in ["dict", "process_list"]:
            super().__setattr__(__name, value)
        else:
            self.dict[__name] = value

    def __delattr__(self, __name: str) -> None:
        """Delete attribute, sub-configuration or parameter.

        The dict should be nested (unflattened). If it is not the case,
        you can apply :func:`dict_routines.flatten` on ``config.dict``
        to unflatten it.
        """
        if __name in ["dict", "process_list"]:
            super().__delattr__(__name)
        else:
            del self.dict[__name]
