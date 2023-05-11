"""Tests for config.py."""
import sys

import pytest
import pytest_check as check

from cliconfig.build_config import load_config, make_config


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
    config, _ = make_config(
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
    check.equal(config, expected_config)
    check.equal(out, expected_out)

    # No additional configs
    sys.argv = [
        "tests/test_make_config.py.py",
    ]
    config, _ = make_config(
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
    check.equal(config, expected_config)

    sys.argv = sys_argv.copy()


def test_load_config() -> None:
    """Test and load_config."""
    # With default configs
    config, _ = load_config(
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
    check.equal(config, expected_config)
    # Additional keys when allow_new_keys=False
    with pytest.raises(ValueError, match="New parameter found 'param3'.*"):
        load_config(
            "tests/configs/default2.yaml",
            default_config_paths=[
                "tests/configs/default1.yaml",
            ],
        )
