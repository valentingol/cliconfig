"""Shared pytest fixtures."""
from typing import Any, Dict

import pytest

from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_all_tags, clean_tag


class ProcessAdd1(Processing):
    """Add 1 to values with tag "@add1"."""

    # pylint: disable=unused-argument
    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, value in items:
            end_key = flat_key.split(".")[-1]
            if "@add1" in end_key:
                flat_dict[clean_tag(flat_key, "add1")] = value + 1
                del flat_dict[flat_key]
        return flat_dict

    def presave(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list
    ) -> Dict[str, Any]:
        """Pre-save processing."""
        return self.premerge(flat_dict, processing_list)


class ProcessKeep(Processing):
    """Prevent a value from being changed after the merge."""

    def __init__(self) -> None:
        super().__init__()
        self.keep_vals: Dict[str, Any] = {}

    # pylint: disable=unused-argument
    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, value in items:
            end_key = flat_key.split(".")[-1]
            if "@keep" in end_key:
                new_key = clean_tag(flat_key, "keep")
                flat_dict[new_key] = value
                del flat_dict[flat_key]
                self.keep_vals[clean_all_tags(flat_key)] = value
        return flat_dict

    # pylint: disable=unused-argument
    def postmerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Post-merge processing."""
        for key, value in self.keep_vals.items():
            if key in flat_dict:
                flat_dict[key] = value
        self.keep_vals = {}
        return flat_dict

    # pylint: disable=unused-argument
    def postload(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Post-load processing."""
        for key, value in self.keep_vals.items():
            flat_dict[key] = value
        self.keep_vals = {}
        return flat_dict


@pytest.fixture()
def process_add1() -> ProcessAdd1:
    """Return a processing object that adds 1 on tag "@add1"."""
    return ProcessAdd1()


@pytest.fixture()
def process_keep() -> ProcessKeep:
    """Return a processing object that keep a value unchanged after the merge."""
    return ProcessKeep()
