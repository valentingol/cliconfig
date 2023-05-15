"""Test base class of configuration."""

import pytest_check as check

from cliconfig.base import Config
from cliconfig.processing.base import Processing


def test_config(process_add1: Processing) -> None:
    """Test base class of configuration."""
    config_dict = {"a.b": 1, "b": 2, "c.d.e": 3, "c.d.f": [2, 3]}
    config = Config(config_dict, [process_add1])
    check.equal(config.dict, config_dict)
    check.equal(config.process_list, [process_add1])
    check.equal(repr(config), f"Config({config_dict}, ['ProcessAdd1'])")
    config_dict2 = {"c.d.e": 3, "a.b": 1, "b": 2, "c.d.f": [2, 3]}
    config2 = Config(config_dict2, [process_add1])
    check.equal(config, config2)
    config3 = Config(config_dict2, [process_add1, process_add1])
    check.not_equal(config, config3)
    config4 = Config(config_dict2, [])
    check.not_equal(config, config4)
