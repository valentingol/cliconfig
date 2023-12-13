"""Tests for config.py."""
import os
import shutil
import sys

import pytest
import pytest_check as check

from cliconfig.base import Config
from cliconfig.config_routines import (
    flatten_config,
    load_config,
    make_config,
    save_config,
    show_config,
    unflatten_config,
    update_config,
)
from cliconfig.processing.base import Processing


def test_make_config(capsys: pytest.CaptureFixture, process_add1: Processing) -> None:
    """Test make_config."""
    sys_argv = sys.argv.copy()
    sys.argv = [
        "tests/test_make_config.py.py",
        "--config",
        "tests/configs/config1.yaml,tests/configs/config2.yaml",
        "--unknown",
        "--param2@add1=6",
        "--unknown2=8",  # check that not error but a warning in console
    ]
    capsys.readouterr()  # Clear stdout and stderr
    config = make_config(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml",
        process_list=[process_add1],
        fallback="tests/configs/fallback.yaml",
    )
    captured = capsys.readouterr()
    out = captured.out
    expected_config = {
        "param1": 4,
        "param2": 7,
        "param3": 3,
        "letters": {
            "letter1": "f",
            "letter2": "e",
            "letter3": "c",
            "letter4": "d",
        },
        "processing name": "ProcessAdd1",
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

    # No additional configs and fallback
    sys.argv = [
        "tests/test_make_config.py.py",
    ]
    config = make_config(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml",
        fallback="tests/configs/fallback.yaml",
    )
    expected_config = {
        "param1": 1,
        "param2": -1,
        "param3": 3,
        "letters": {
            "letter1": "z",
            "letter2": "b",
            "letter3": "c",
            "letter4": "d",
        },
    }
    check.equal(config.dict, expected_config)
    config = make_config(add_default_processing=False)
    check.equal(config.dict, {})
    check.equal(config.process_list, [])

    # No CLI
    sys.argv = [
        "tests/test_make_config.py.py",
        "--config",
        "tests/configs/config1.yaml",
        "--param2=6",
    ]
    config = make_config(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml",
        fallback="tests/configs/fallback.yaml",
        no_cli=True,
    )
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

    # @new in CLI
    sys.argv = [
        "tests/test_make_config.py.py",
        "--unknown@new=0",
    ]
    config = make_config(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml",
    )
    check.equal(config.unknown, 0)

    sys.argv = sys_argv.copy()


def test_load_config(process_add1: Processing) -> None:
    """Test and load_config."""
    # With default configs
    config = load_config(
        "tests/configs/config2.yaml",
        default_config_paths=[
            "tests/configs/default1.yaml",
            "tests/configs/default2.yaml",
        ],
        process_list=[process_add1],
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
        "processing name": "ProcessAdd1",
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


def test_flatten_config() -> None:
    """Test flatten_config."""
    config = Config({"a": 1, "b": {"c": 2, "d": 3}, "e": "f"}, [])
    flat_config = flatten_config(config)
    expected_dict = {"a": 1, "b.c": 2, "b.d": 3, "e": "f"}
    check.equal(flat_config.dict, expected_dict)


def test_unflatten_config() -> None:
    """Test unflatten_config."""
    config = Config({"a": 1, "b.c": 2, "b.d": 3, "e": "f"}, [])
    flat_config = unflatten_config(config)
    expected_dict = {"a": 1, "b": {"c": 2, "d": 3}, "e": "f"}
    check.equal(flat_config.dict, expected_dict)


def test_update_config() -> None:
    """Test update_config."""
    config = Config({"a": 1, "b": {"c": 2, "d": 3}, "e": "f"}, [])
    new_dict = {"b": {"c": 3}, "g": "h"}
    new_config = update_config(config, new_dict)
    expected_dict = {"a": 1, "b": {"c": 3, "d": 3}, "e": "f", "g": "h"}
    check.equal(new_config.dict, expected_dict)
