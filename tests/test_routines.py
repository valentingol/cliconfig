"""Tests for build.py."""
import pytest
import pytest_check as check

from cliconfig.routines import (
    _del_key,
    clean_pre_flat,
    flat_config,
    merge_config,
    merge_config_file,
    unflat_config,
)


def test_merge_config() -> None:
    """Test merge_config."""
    config1 = {"a.b": 1, "a": {"c": 2}}
    config2 = {"c": 3}
    config = merge_config(config1, config2, allow_new_keys=True)
    check.equal(config, {"a": {"b": 1, "c": 2}, "c": 3})
    with pytest.raises(ValueError, match="New parameter found 'c'.*"):
        merge_config(config1, config2, allow_new_keys=False)
    config1 = {"a.b": 1, "a": {"b": 1, "c": 2}}
    with pytest.raises(
        ValueError,
        match="Duplicated key found.*You may consider calling `clean_pre_flat`.*",
    ):
        merge_config(config1, config2, allow_new_keys=True)


def test_merge_config_file() -> None:
    """Test merge_config."""
    config1 = {
        "param1": 1,
        "param2": 2,
        "letters": {
            "letter1": "a",
            "letter2": "b",
        },
    }
    config2 = {
        "param3": 3,
        "letters": {
            "letter3": "c",
            "letter4": "d",
        },
    }
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

    config = merge_config_file(
        "tests/configs/default1.yaml",
        "tests/configs/default2.yaml",
        allow_new_keys=True,
    )
    check.equal(config, expected_config)
    config = merge_config_file(config1, config2, allow_new_keys=True)
    check.equal(config, expected_config)
    config = merge_config_file(
        config1, "tests/configs/default2.yaml", allow_new_keys=True
    )
    check.equal(config, expected_config)
    with pytest.raises(ValueError, match="New parameter found 'param3'.*"):
        merge_config_file(
            "tests/configs/default1.yaml",
            "tests/configs/default2.yaml",
            allow_new_keys=False,
        )


def test_flat_config() -> None:
    """Test flat_config."""
    check.equal(
        flat_config({"a.b": 1, "a": {"c": 2}, "d": 3}),
        {"a.b": 1, "a.c": 2, "d": 3},
    )
    check.equal(
        flat_config({"a.b": 1, "a": {"c": {}}, "a.c": 3}),
        {"a.b": 1, "a.c": 3},
    )
    with pytest.raises(ValueError, match="duplicated key 'a.b'"):
        flat_config({"a.b": 1, "a": {"b": 1}})


def test_unflat_config() -> None:
    """Test unflat_config."""
    check.equal(
        unflat_config({"a.b": 1, "a.c": 2, "c": 3}),
        {"a": {"b": 1, "c": 2}, "c": 3},
    )
    with pytest.raises(ValueError, match="The config must be flatten.*"):
        unflat_config({"a.b": 1, "a": {"c": 2}})


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


def test_del_key() -> None:
    """Test _del_key."""
    check.equal(
        _del_key({"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}, "a.b.c"),
        {"a": {"d": 2}, "a.e": 3},
    )
    check.equal(
        _del_key(
            {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4},
            "a.b.c",
            keep_flat=True,
        ),
        {"a": {"d": 2}, "a.e": 3, "a.b.c": 4},
    )
    check.equal(
        _del_key(
            {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4},
            "a.b.c",
            keep_unflat=True,
        ),
        {"a": {"b": {"c": 1}, "d": 2}, "a.e": 3},
    )
    with pytest.raises(ValueError, match="Key 'a.b.z' not found in config."):
        _del_key({"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}, "a.b.z")
    with pytest.raises(ValueError, match="Key 'a.z.c' not found in config."):
        _del_key({"a": {"b": {"c": 1}, "d": 2}, "a.e": 3, "a.b.c": 4}, "a.z.c")
