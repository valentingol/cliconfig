"""Tests for dict routines."""
import os
import shutil

import pytest
import pytest_check as check

from cliconfig.dict_routines import (
    _del_key,
    clean_pre_flat,
    flatten,
    load_dict,
    merge_flat,
    merge_flat_paths,
    save_dict,
    show_dict,
    unflatten,
)


def test_flatten() -> None:
    """Test flatten(."""
    check.equal(
        flatten({"a.b": 1, "a": {"c": 2}, "d": 3}),
        {"a.b": 1, "a.c": 2, "d": 3},
    )
    check.equal(
        flatten({"a.b": {"c": 1}, "a": {"b.d": 2}, "a.e": {"f.g": 3}}),
        {"a.b.c": 1, "a.b.d": 2, "a.e.f.g": 3},
    )
    check.equal(
        flatten({"a.b": 1, "a": {"c": {}}, "a.c": 3}),
        {"a.b": 1, "a.c": 3},
    )
    with pytest.raises(ValueError, match="duplicated key 'a.b'"):
        flatten({"a.b": 1, "a": {"b": 1}})


def test_unflatten() -> None:
    """Test unflatten."""
    check.equal(
        unflatten({"a.b": 1, "a.c": 2, "c": 3}),
        {"a": {"b": 1, "c": 2}, "c": 3},
    )
    with pytest.raises(ValueError, match="The dict must be flatten.*"):
        unflatten({"a.b": 1, "a": {"c": 2}})


def test_merge_flat() -> None:
    """Test merge_flat."""
    dict1 = {"a.b": 1, "a": {"c": 2}}
    dict2 = {"c": 3}
    check.equal(
        merge_flat(dict1, dict2, allow_new_keys=True),
        {"a.b": 1, "a.c": 2, "c": 3},
    )
    with pytest.raises(ValueError, match="New parameter found 'c'.*"):
        merge_flat(dict1, dict2, allow_new_keys=False)
    dict1 = {"a.b": 1, "a": {"b": 1, "c": 2}}
    with pytest.raises(
        ValueError,
        match="Duplicated key found.*You may consider calling 'clean_pre_flat'.*",
    ):
        merge_flat(dict1, dict2, allow_new_keys=True)


def test_merge_flat_paths() -> None:
    """Test merge_flat_paths."""
    dict1 = {
        "param1": 1,
        "param2": 2,
        "letters": {
            "letter1": "a",
            "letter2": "b",
        },
    }
    dict2 = {
        "param3": 3,
        "letters": {
            "letter3": "c",
            "letter4": "d",
        },
    }
    expected_dict = {
        "param1": 1,
        "param2": 2,
        "param3": 3,
        "letters.letter1": "a",
        "letters.letter2": "b",
        "letters.letter3": "c",
        "letters.letter4": "d",
    }

    flat_dict = merge_flat_paths(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml",
        allow_new_keys=True,
    )
    check.equal(flat_dict, expected_dict)
    flat_dict = merge_flat_paths(dict1, dict2, allow_new_keys=True)
    check.equal(flat_dict, expected_dict)
    flat_dict = merge_flat_paths(
        dict1, "tests/configs/default2.yaml", allow_new_keys=True
    )
    check.equal(flat_dict, expected_dict)
    with pytest.raises(ValueError, match="New parameter found 'param3'.*"):
        merge_flat_paths(
            "tests/configs/default1.yaml",
            "tests/configs/default2.yaml",
            allow_new_keys=False,
        )


def test_del_key() -> None:
    """Test _del_key."""
    in_dict = {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}
    _del_key(in_dict, "a.b.c")
    check.equal(in_dict, {"a": {"d": 2}, "a.e": 3})

    in_dict = {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}
    _del_key(in_dict, "a.b.c", keep_flat=True)
    check.equal(in_dict, {"a": {"d": 2}, "a.e": 3, "a.b.c": 4})

    in_dict = {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}
    _del_key(in_dict, "a.b.c", keep_unflat=True)
    check.equal(in_dict, {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3})

    with pytest.raises(ValueError, match="Key 'a.b.z' not found in dict."):
        _del_key({"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}, "a.b.z")
    with pytest.raises(ValueError, match="Key 'a.z.c' not found in dict."):
        _del_key({"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}, "a.z.c")


def test_clean_pre_flat() -> None:
    """Test clean_pre_flat."""
    check.equal(
        clean_pre_flat({"a.b": 1, "a": {"b": 2}, "c": 3}, priority="flat"),
        {"a.b": 1, "c": 3},
    )
    check.equal(
        clean_pre_flat({"a.b": 1, "a": {"b": 2}, "c": 3}, priority="unflat"),
        {"a": {"b": 2}, "c": 3},
    )
    with pytest.raises(ValueError, match="duplicated key 'a.b'"):
        clean_pre_flat({"a.b": 1, "a": {"b": 2}, "c": 3}, priority="error")
    with pytest.raises(
        ValueError,
        match=(
            "priority argument must be one of 'flat', 'unflat' or 'error' but "
            "found 'UNKNOWN'"
        ),
    ):
        clean_pre_flat({"a.b": 1, "a": {"b": 2}, "c": 3}, priority="UNKNOWN")


def test_save_load_dict() -> None:
    """Test save_dict and load_dict."""
    dict1 = {"a": 1, "b": {"c": 2}, "d": [2, 3.0], "e": [{"f": 4}]}
    save_dict(dict1, "tests/tmp/config.yaml")
    check.is_true(os.path.isfile("tests/tmp/config.yaml"))
    dict2 = load_dict("tests/tmp/config.yaml")
    check.equal(dict1, dict2)
    # Case multiple files and yaml tags
    out_dict = load_dict("tests/configs/multi_files_with_tags.yaml")
    expected_dict = {
        "config@cfg": {
            "param1@par@other": 1,
            "param2": {"a": 1.0, "b@par2": "2.1"},
        },
        "config2": {
            "param3@par3": 3.2,
            "param4@par4": [4, 5, {"6": 6}],
            "param5": [True, 8],
        },
        "config3@cfg3": {"param6": {"param7@par7": None}, "param8": "True"},
        "config4@cfg4": {"config5@cfg5": {"param9": "11"}},
    }
    check.equal(out_dict, expected_dict)
    shutil.rmtree("tests/tmp")


def test_show_dict() -> None:
    """Test show_dict."""
    in_dict = {
        "model": {
            "s1_ae_config": {
                "in_dim": 2,
                "out_dim": 1,
                "layer_channels": [16, 32, 64],
                "conv_per_layer": 1,
                "residual": False,
                "dropout_rate": 0.0,
            },
            "mask_module_dim": [6, 2],
            "glob_module_dims": [2, 8, 2],
            "conv_block_dims": [32, 64, 128],
        },
        "train": {
            "n_epochs": 100,
            "optimizer": {
                "name": "Adam",
                "lr": 0.001,
                "weight_decay": 0.0,
                "warmup_steps": 0,
            },
        },
        "data": {
            "dataset": "mnist",
            "batch_size": 128,
            "num_workers": 6,
        },
    }
    show_dict(in_dict)
