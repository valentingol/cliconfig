"""Tests for dict routines with preprocessing."""
import shutil

import pytest_check as check
import yaml

from cliconfig.process_routines import (
    load_processing,
    merge_flat_paths_processing,
    merge_flat_processing,
    save_processing,
)
from cliconfig.processing.base import Processing
from tests.conftest import ProcessAdd1, ProcessKeep


def test_processing() -> None:
    """Test Processing."""
    in_dict = {"a.b": 1, "b": 2, "c.d.e": 3, "c.d.f": [2, 3]}
    base_process = Processing()
    check.equal(
        (
            base_process.premerge(in_dict, []),
            base_process.postmerge(in_dict, []),
            base_process.presave(in_dict, []),
            base_process.postload(in_dict, []),
        ),
        (in_dict, in_dict, in_dict, in_dict),
    )


def test_merge_flat_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test merge_flat_processing."""
    dict1 = {"a": {"b": 1, "c": 2, "d@keep": 3}}
    dict2 = {"a": {"b": 2, "c@add1": 3, "d": 4}}
    flat_dict, processing_list = merge_flat_processing(
        dict1,
        dict2,
        processing_list=[process_add1, process_keep],
        allow_new_keys=False,
    )
    check.equal(
        flat_dict,
        {"a.b": 2, "a.c": 4, "a.d": 3},
    )
    check.equal(processing_list, [process_add1, process_keep])
    check.equal(process_keep.keep_vals, {})


def test_merge_flat_paths_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test merge_flat_paths_processing."""
    dict1 = {"param1@add1": 0, "param2.param3@keep": 1}
    dict2 = {"param2.param3": 3}
    expected_dict = {"param1": 1, "param2.param3": 1}
    check.equal(
        merge_flat_paths_processing(
            "tests/configs/configtag1.yaml",
            "tests/configs/configtag2.yaml",
            [process_add1, process_keep],
            allow_new_keys=False,
        ),
        (expected_dict, [process_add1, process_keep]),
    )
    check.equal(
        merge_flat_paths_processing(
            dict1,
            dict2,
            [process_add1, process_keep],
            allow_new_keys=False,
        ),
        (expected_dict, [process_add1, process_keep]),
    )
    check.equal(process_keep.keep_vals, {})


def test_save_processing(
    process_add1: ProcessAdd1,
    process_keep: ProcessKeep,
) -> None:
    """Test save_processing."""
    in_dict = {"param1@add1": 0, "param2.param3@add1": 1}
    save_processing(in_dict, "tests/tmp/config.yaml", [process_add1, process_keep])
    with open("tests/tmp/config.yaml", "r", encoding="utf-8") as yaml_file:
        loaded_dict = yaml.safe_load(yaml_file)
    check.equal(loaded_dict, {"param1": 1, "param2.param3": 2})
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
    check.equal(config, {"param2.param3": 0})
