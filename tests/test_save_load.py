"""Tests for save_load.py."""
import os
import shutil

import pytest
import pytest_check as check

from cliconfig.save_load import load_config, save_config


def test_save_load_config() -> None:
    """Test save_config and load_config."""
    config1 = {"a": 1, "b": {"c": 2}, "d": [2, 3.0], "e": [{"f": 4}]}
    save_config(config1, "tests/tmp/config.yaml")
    check.is_true(os.path.isfile("tests/tmp/config.yaml"))
    config2 = load_config("tests/tmp/config.yaml")
    check.equal(config1, config2)

    # With default configs
    config = {"param1": 3, "param2": 4, "letters": {"letter1": "e"}}
    save_config(config, "tests/tmp/config2.yaml")
    config = load_config(
        "tests/tmp/config2.yaml",
        default_config_paths=[
            "tests/configs/default1.yaml",
            "tests/configs/default2.yaml",
        ],
        allow_new_keys=False,
    )
    expected_config = {
        "param1": 3,
        "param2": 4,
        "param3": 3,
        "letters": {
            "letter1": "e",
            "letter2": "b",
            "letter3": "c",
            "letter4": "d",
        },
    }
    check.equal(config, expected_config)
    # Additional keys when allow_new_keys=False
    config = {"param4": 0}
    save_config(config, "tests/tmp/config3.yaml")
    with pytest.raises(ValueError, match="New parameter found 'param4'.*"):
        load_config(
            "tests/tmp/config3.yaml",
            default_config_paths=[
                "tests/configs/default1.yaml",
                "tests/configs/default2.yaml",
            ],
            allow_new_keys=False,
        )

    shutil.rmtree("tests/tmp")
