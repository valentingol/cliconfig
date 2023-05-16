"""Shared pytest fixtures."""
from typing import Any, Dict

import pytest

from cliconfig.base import Config
from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_all_tags, clean_tag, is_tag_in


class ProcessAdd1(Processing):
    """Add 1 to values with tag "@add1"."""

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "add1"):
                flat_config.dict[clean_tag(flat_key, "add1")] = value + 1
                del flat_config.dict[flat_key]
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing."""
        flat_config.dict["processing name"] = "ProcessAdd1"
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        return self.premerge(flat_config)


class ProcessKeep(Processing):
    """Prevent a value from being changed after the merge."""

    def __init__(self) -> None:
        super().__init__()
        self.keep_vals: Dict[str, Any] = {}

    # pylint: disable=unused-argument
    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "keep"):
                new_key = clean_tag(flat_key, "keep")
                flat_config.dict[new_key] = value
                del flat_config.dict[flat_key]
                self.keep_vals[clean_all_tags(flat_key)] = value
        return flat_config

    # pylint: disable=unused-argument
    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        for key, value in self.keep_vals.items():
            if key in flat_config.dict:
                flat_config.dict[key] = value
        self.keep_vals = {}
        return flat_config

    # pylint: disable=unused-argument
    def postload(self, flat_config: Config) -> Config:
        """Post-load processing."""
        for key, value in self.keep_vals.items():
            flat_config.dict[key] = value
        self.keep_vals = {}
        return flat_config


@pytest.fixture()
def process_add1() -> ProcessAdd1:
    """Return a processing object that adds 1 on tag "@add1"."""
    return ProcessAdd1()


@pytest.fixture()
def process_keep() -> ProcessKeep:
    """Return a processing object that keep a value unchanged after the merge."""
    return ProcessKeep()
