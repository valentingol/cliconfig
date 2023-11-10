"""Tests for dict routines with preprocessing."""
import re
import shutil

import pytest
import pytest_check as check
import yaml

from cliconfig.base import Config
from cliconfig.process_routines import (
    end_build_processing,
    load_processing,
    merge_flat_paths_processing,
    merge_flat_processing,
    save_processing,
)
from cliconfig.processing.base import Processing
from tests.conftest import ProcessAdd1, ProcessKeep


def test_merge_flat_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test merge_flat_processing."""

    class _ProcessingTest(Processing):
        def __init__(self) -> None:
            super().__init__()
            self.attr = 0

    proc1 = _ProcessingTest()
    proc2 = _ProcessingTest()
    proc2.attr = 1
    proc3 = _ProcessingTest()

    config1 = Config({"a": {"b": 1, "c": 2, "d@keep": 3}}, [proc1, proc2, process_add1])
    config2 = Config({"a": {"b": 2, "c@add1": 3, "d": 4}}, [proc3, process_keep])
    config = merge_flat_processing(
        config1,
        config2,
        allow_new_keys=False,
    )
    check.equal(
        config.dict,
        {"a.b": 2, "a.c": 4, "a.d": 3},
    )
    check.equal(config.process_list, [proc1, proc2, process_add1, process_keep])
    check.equal(process_keep.keep_vals, {})


def test_merge_flat_paths_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test merge_flat_paths_processing."""
    config1 = Config(
        {"param1@add1": 0, "param2.param3@keep": 1}, [process_add1, process_keep]
    )
    config2 = Config({"param2.param3": 3}, [])
    expected_dict = {"param1": 1, "param2.param3": 1}
    check.equal(
        merge_flat_paths_processing(
            "tests/configs/configtag1.yaml",
            "tests/configs/configtag2.yaml",
            allow_new_keys=False,
            additional_process=[process_add1, process_keep],
        ),
        Config(expected_dict, [process_add1, process_keep]),
    )
    check.equal(
        merge_flat_paths_processing(
            config1,
            config2,
            allow_new_keys=False,
        ),
        Config(expected_dict, [process_add1, process_keep]),
    )
    check.equal(process_keep.keep_vals, {})

    # Case with dict in input


def test_save_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test save_processing."""
    config = Config(
        {"param1@add1": 0, "param2.param3@add1": 1}, [process_add1, process_keep]
    )
    save_processing(config, "tests/tmp/config.yaml")
    check.equal(config.dict["param1@add1"], 0)
    check.is_not_in("param1", config.dict)
    with open("tests/tmp/config.yaml", "r", encoding="utf-8") as yaml_file:
        loaded_dict = yaml.safe_load(yaml_file)
    check.equal(loaded_dict, {"param1": 1, "param2": {"param3": 2}})
    check.equal(process_keep.keep_vals, {})
    shutil.rmtree("tests/tmp")


def test_load_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test load_processing."""
    process_keep.keep_vals = {"param2.param3": 0}
    config = load_processing(
        "tests/configs/configtag2.yaml",
        [process_add1, process_keep],
    )
    check.equal(config.dict, {"param2.param3": 0})
    with pytest.raises(
        ValueError,
        match=re.escape(
            "config_or_path must be a Config instance or a path to a yaml file "
            "but you passed a dict. If you want to use it as a valid input, "
            "you should use Config(<input dict>, []) instead."
        ),
    ):
        merge_flat_paths_processing(
            {"a": 2},  # type: ignore
            Config({"a": 1}, []),
        )
    with pytest.raises(
        ValueError,
        match=("config_or_path must be a Config instance or a path to a yaml file."),
    ):
        merge_flat_paths_processing(
            Config({"a": 1}, []),
            ("not a path",),  # type: ignore
        )


def test_end_build_processing(process_add1: ProcessAdd1) -> None:
    """Test end_build_processing."""
    config = Config({"param1@add1": 0}, [process_add1])
    config = end_build_processing(config)
    check.equal(config.dict, {"param1@add1": 0, "processing name": "ProcessAdd1"})
