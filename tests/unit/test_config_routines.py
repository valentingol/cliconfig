"""Tests for config.py."""
import os
import shutil
import sys

import pytest
import pytest_check as check

from cliconfig.base import Config
from cliconfig.config_routines import load_config, make_config, save_config, show_config


def test_make_config(capsys: pytest.CaptureFixture) -> None:
    """Test make_config."""
    sys_argv = sys.argv.copy()
    sys.argv = [
        "tests/test_make_config.py.py",
        "--config",
        "tests/configs/config1.yaml,tests/configs/config2.yaml",
        "--unknown",
        "--param2=6",
        "--unknown2=8",  # check that not error but a warning in console
    ]
    capsys.readouterr()  # Clear stdout and stderr
    config = make_config(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml"
    )
    captured = capsys.readouterr()
    out = captured.out
    expected_config = {
        "param1": 4,
        "param2": 6,
        "param3": 3,
        "letters": {
            "letter1": "f",
            "letter2": "e",
            "letter3": "c",
            "letter4": "d",
        },
    }
    expected_out = (
        "[CONFIG] Warning: New keys found in CLI parameters that will not be merged:\n"
        "  - unknown\n"
        "  - unknown2\n"
        "[CONFIG] Info: Merged 2 default config(s), "
        "2 additional config(s) and 1 CLI parameter(s).\n"
    )
    check.equal(config.dict, expected_config)
    check.equal(out, expected_out)

    # No additional configs
    sys.argv = [
        "tests/test_make_config.py.py",
    ]
    config = make_config(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml")
    expected_config = {
        "param1": 1,
        "param2": 2,
        "param3": 3,
        "letters": {
            "letter1": "a",
            "letter2": "b",
            "letter3": "c",
            "letter4": "d",
        },
    }
    check.equal(config.dict, expected_config)

    sys.argv = sys_argv.copy()


def test_load_config() -> None:
    """Test and load_config."""
    # With default configs
    config = load_config(
        "tests/configs/config2.yaml",
        default_config_paths=[
            "tests/configs/default1.yaml",
            "tests/configs/default2.yaml",
        ]
    )
    expected_config = {
        "param1": 4,
        "param2": 2,
        "param3": 3,
        "letters": {
            "letter1": "a",
            "letter2": "e",
            "letter3": "c",
            "letter4": "d",
        },
    }
    check.equal(config.dict, expected_config)
    # Additional keys when allow_new_keys=False
    with pytest.raises(ValueError, match="New parameter found 'param3'.*"):
        load_config(
            "tests/configs/default2.yaml",
            default_config_paths=[
                "tests/configs/default1.yaml",
            ],
        )


def test_show_config() -> None:
    """Test show_config."""
    show_config(Config({"a": 1, "b": {"c": 2, "d": 3}, "e": "f"}, []))


def test_save_config() -> None:
    """Test save_config."""
    config = Config({"a": 1, "b": {"c": 2, "d": 3}, "e": "f"}, [])
    save_config(config, "tests/tmp/config.yaml")
    check.is_true(os.path.exists("tests/tmp/config.yaml"))
    shutil.rmtree("tests/tmp")
