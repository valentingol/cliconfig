"""Base class for processing."""
from typing import Any, Dict


class Processing():
    """Processing base class."""

    def __init__(self) -> None:
        self.premerge_order = 0.0
        self.postmerge_order = 0.0
        self.presave_order = 0.0
        self.postload_order = 0.0

    # pylint: disable=unused-argument
    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-merge processing.

        Function that can be applied to the flat dict to modify it
        before merging . It takes a flat dict and returns a flat dict.
        """
        return flat_dict

    # pylint: disable=unused-argument
    def postmerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Post-merge processing.

        Function that can be applied to the flat dict to modify it
        after merging . It takes a flat dict and returns a flat dict.
        """
        return flat_dict

    # pylint: disable=unused-argument
    def presave(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-save processing.

        Function applied to the flat dict to modify it before
        saving it. It takes a flat dict and returns a flat dict.
        """
        return flat_dict

    # pylint: disable=unused-argument
    def postload(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Post-load processing.

        Function applied to the flat dict to modify it after
        loading it. It takes a flat dict and returns a flat dict.
        """
        return flat_dict
