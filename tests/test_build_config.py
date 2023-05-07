"""Tests for build_config.py."""
import sys

import pytest
import pytest_check as check

from cliconfig.build_config import make_config


def test_make_config(capsys: pytest.CaptureFixture) -> None:
    """Test make_config."""
    sys_argv = sys.argv.copy()
    sys.argv = [
        "tests/test_make_config.py.py",
        "--config",
        "tests/configs/config1.yaml,tests/configs/config2.yaml",
        "--param2",
        "6",
    ]
    capsys.readouterr()  # Clear stdout and stderr
    config = make_config("tests/configs/default1.yaml", "tests/configs/default2.yaml")
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
        "[CONFIG] Merge 2 default configs, "
        "2 additional configs and 1 CLI parameter(s).\n"
    )
    check.equal(config, expected_config)
    check.equal(out, expected_out)

    # No default configs
    config = make_config(allow_new_keys=True)
    expected_config = {
        "param1": 4,
        "param2": 6,
        "letters": {
            "letter1": "f",
            "letter2": "e",
        },
    }
    check.equal(config, expected_config)

    # No additional configs
    sys.argv = [
        "tests/test_make_config.py.py",
    ]
    config = make_config("tests/configs/default1.yaml", "tests/configs/default2.yaml")
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
