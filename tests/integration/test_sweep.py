# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Integration test for sweep updates."""
import pytest_check as check

from cliconfig import make_config, update_config


def test_sweep() -> None:
    """Integration test for sweep."""
    config = make_config("tests/configs/integration/sweep.yaml", no_cli=True)
    expected_dict = {
        "args": {"a": 5, "b": 3, "c": True, "d": [1, 0]},
        "res": [1, 0, 3, 6],
    }
    check.equal(config.dict, expected_dict)

    config = update_config(
        config, {"args": {"a": 2, "b": 7, "c": False, "d": [1, 2, 3]}}
    )
    expected_dict = {
        "args": {"a": 2, "b": 7, "c": False, "d": [1, 2, 3]},
        "res": [1, 2, 3, 0, 7],
    }
    check.equal(config.dict, expected_dict)
    config = update_config(config, {"args": {"a": 2}, "res": 5})
    check.equal(config.res, 5)
    config = update_config(config, {"args": {"a": 3}})
    check.equal(config.res, 5)
