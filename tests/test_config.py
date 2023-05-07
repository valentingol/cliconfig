"""Tests for config.py."""
import os
import shutil
import sys

import pytest
import pytest_check as check

from cliconfig import load_config, make_config, merge, save_config


def test_merge() -> None:
    """Test merge."""
    config1 = {'a.b': 1, 'a': {'b': 2, 'c': 3}}
    config2 = {'a': {'c': 1}, 'a.d': 6}
    config = merge(config1, config2, allow_new_keys=True, priority='flat')
    check.equal(config, {'a': {'b': 1, 'c': 1, 'd': 6}})
    config = merge(config1, config2, allow_new_keys=True, priority='unflat')
    check.equal(config, {'a': {'b': 2, 'c': 1, 'd': 6}})
    with pytest.raises(ValueError, match="New parameter 'a.d' found.*"):
        merge(config1, config2, allow_new_keys=False)
    with pytest.raises(ValueError, match="Unknown dot_prior 'UNKONWN'.*"):
        merge(config1, config2, allow_new_keys=True, priority='UNKONWN')


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
    config = make_config('tests/configs/default1.yaml',
                         'tests/configs/default2.yaml')
    captured = capsys.readouterr()
    out = captured.out
    expected_config = {
        'param1': 4,
        'param2': 6,
        'param3': 3,
        'letters': {
            'letter1': 'f',
            'letter2': 'e',
            'letter3': 'c',
            'letter4': 'd',
        },
    }
    expected_out = ("[CONFIG] Merge 2 default configs, "
                    "2 additional configs and 1 CLI parameter(s).\n")
    check.equal(config, expected_config)
    check.equal(out, expected_out)

    # No default configs
    config = make_config(allow_new_keys=True)
    expected_config = {
        'param1': 4,
        'param2': 6,
        'letters': {
            'letter1': 'f',
            'letter2': 'e',
        },
    }
    check.equal(config, expected_config)

    # No additional configs
    sys.argv = [
        "tests/test_make_config.py.py",
    ]
    config = make_config('tests/configs/default1.yaml',
                         'tests/configs/default2.yaml')
    expected_config = {
        'param1': 1,
        'param2': 2,
        'param3': 3,
        'letters': {
            'letter1': 'a',
            'letter2': 'b',
            'letter3': 'c',
            'letter4': 'd',
        },
    }
    check.equal(config, expected_config)

    sys.argv = sys_argv.copy()


def test_save_load_config() -> None:
    """Test save_config and load_config."""
    config1 = {'a': 1, 'b': {'c': 2}, 'd': [2, 3.0], 'e': [{'f': 4}]}
    save_config(config1, 'tests/tmp/config.yaml')
    check.is_true(os.path.isfile('tests/tmp/config.yaml'))
    config2 = load_config('tests/tmp/config.yaml')
    check.equal(config1, config2)

    # With default configs
    config = {'param1': 3, 'param2': 4, 'letters': {'letter1': 'e'}}
    save_config(config, 'tests/tmp/config2.yaml')
    config = load_config(
        'tests/tmp/config2.yaml',
        default_configs=['tests/configs/default1.yaml', 'tests/configs/default2.yaml'],
        allow_new_keys=False,
    )
    expected_config = {
        'param1': 3,
        'param2': 4,
        'param3': 3,
        'letters': {
            'letter1': 'e',
            'letter2': 'b',
            'letter3': 'c',
            'letter4': 'd',
        },
    }
    check.equal(config, expected_config)
    # Additional keys when allow_new_keys=False
    config = {'param4': 0}
    save_config(config, 'tests/tmp/config3.yaml')
    with pytest.raises(ValueError, match="New parameter 'param4' found.*"):
        load_config(
            'tests/tmp/config3.yaml',
            default_configs=['tests/configs/default1.yaml',
                             'tests/configs/default2.yaml'],
            allow_new_keys=False,
        )

    shutil.rmtree('tests/tmp')
