"""Test base class of configuration."""

import pytest_check as check

from cliconfig.base import Config
from cliconfig.dict_routines import unflatten
from cliconfig.processing.base import Processing


def test_config(process_add1: Processing) -> None:
    """Test base class of configuration."""
    config_dict = {"a.b": 1, "b": 2, "c.d.e": 3, "c.d.f": [2, 3]}
    config_dict = unflatten(config_dict)
    config = Config(config_dict, [process_add1])
    check.equal(config.dict, config_dict)
    check.equal(config.process_list, [process_add1])
    check.equal(repr(config), f"Config({config_dict}, ['ProcessAdd1'])")
    config_dict2 = {"c.d.e": 3, "a.b": 1, "b": 2, "c.d.f": [2, 3]}
    config_dict2 = unflatten(config_dict2)
    config2 = Config(config_dict2, [process_add1])
    check.equal(config, config2)
    config3 = Config(config_dict2, [process_add1, process_add1])
    check.not_equal(config, config3)
    config4 = Config(config_dict2, [])
    check.not_equal(config, config4)
    # Test get/set attribute
    config = Config(config_dict, [process_add1])
    check.equal(config.a.b, 1)
    check.equal(config.c.d.f, [2, 3])
    check.equal(config.c.d, Config({"e": 3, "f": [2, 3]}, [process_add1]))
    config.a.b = 2
    check.equal(config.a.b, 2)
    config.c.d.f = [3, 4]
    check.equal(config.c.d.f, [3, 4])
    config.c.d.f.append(5)
    check.equal(config.c.d.f, [3, 4, 5])
    # Test delete attribute
    del config.a.b
    check.equal(config.dict, {"a": {}, "b": 2, "c": {"d": {"e": 3, "f": [3, 4, 5]}}})
    del config.c.d
    check.equal(config.dict, {"a": {}, "b": 2, "c": {}})
    # Should no raise error
    del config.dict
    del config.process_list
