"""Base class for processing."""
# pylint: disable=attribute-defined-outside-init
from typing import Any, Dict


class Processing():
    """Processing base class."""

    def __init__(self) -> None:
        self.premerge_order = 0.0
        self.postmerge_order = 0.0
        self.presave_order = 0.0
        self.postload_order = 0.0
        # Create a list_processing attribute if your processing needs to use
        # processing routines (merge_flat_processing, save_processing, load_processing)

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
        if hasattr(self, 'list_processing'):
            # Update the list processing to pass it to the next processing
            self.list_processing = processing_list  # noqa
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
        if hasattr(self, 'list_processing'):
            # Update the list processing to pass it to the next processing
            self.list_processing = processing_list
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
        if hasattr(self, 'list_processing'):
            # Update the list processing to pass it to the next processing
            self.list_processing = processing_list
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
        if hasattr(self, 'list_processing'):
            # Update the list processing to pass it to the next processing
            self.list_processing = processing_list
        return flat_dict
