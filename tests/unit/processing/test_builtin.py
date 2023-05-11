"""Test built-in processing classes."""
import re

import pytest
import pytest_check as check

from cliconfig.dict_routines import flatten
from cliconfig.processing.builtin import (
    ProcessCheckTags,
    ProcessCopy,
    ProcessMerge,
    ProcessTyping,
)


def test_process_merge() -> None:
    """Test ProcessMerge."""
    # Test @merge_add
    processing = ProcessMerge()
    flat_dict = {
        "config1.param1": 0,
        "config1.param2": 1,
        "config2_path@merge_add": "tests/configs/merge/default2.yaml",
    }
    flat_dict = processing.premerge(flat_dict, [processing])
    expected_dict = {
        "config1.param1": 0,
        "config1.param2": 1,
        "config2.param1": 2,
        "config2.param2": 3,
        "config3.param1": 4,
        "config3.param2": 5,
        "config2_path": "tests/configs/merge/default2.yaml",
        "config3_path": "tests/configs/merge/default3.yaml",
    }
    check.equal(flat_dict, expected_dict)

    # Case of introducing a new key
    flat_dict = {
        "config1.param1": 0,
        "config1.param2": 1,
        "config3.param1": 4,
        "config2_path@merge_add": "tests/configs/merge/default2.yaml",
    }
    with pytest.raises(
        ValueError,
        match=(
            "@merge_add doest not allow to add "
            "already existing keys but key 'config3.param1'.*"
        )
    ):
        processing.premerge(flat_dict, [processing])

    # Test @merge_before and @merge_after
    flat_dict = {
        "a.b": 1,
        "a.b_path@merge_after": "tests/configs/merge/additional2.yaml",
    }
    flat_dict = processing.premerge(flat_dict, [processing])
    expected_dict = {
        "a.b": 2,
        "a.b_path": "tests/configs/merge/additional2.yaml",
        "c_path": "tests/configs/merge/additional3.yaml",
        "c": 3,
    }
    check.equal(flat_dict, expected_dict)
    flat_dict = {
        "a.b": 1,
        "a.b_path@merge_before": "tests/configs/merge/additional2.yaml",
        "c": 3,
    }
    flat_dict = processing.premerge(flat_dict, [processing])
    expected_dict = {
        "a.b": 1,
        "a.b_path": "tests/configs/merge/additional2.yaml",
        "c_path": "tests/configs/merge/additional3.yaml",
        "c": 3,
    }
    check.equal(flat_dict, expected_dict)

    # Not valid path
    for tag in ["merge_before", "merge_after", "merge_add"]:
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Key with '@{tag}' tag must be associated "
                "to a string corresponding to a *yaml* file."
                f"The problem occurs at key: a@{tag}"
            )
        ):
            flat_dict = processing.premerge({f'a@{tag}': 'no_yaml'}, [processing])


def test_process_copy() -> None:
    """Test ProcessCopy."""
    processing = ProcessCopy()
    flat_dict = {
        "config1.param1": 1,
        "config2.param2@copy": 'config1.param1',
    }
    flat_dict = processing.premerge(flat_dict, [processing])
    check.equal(flat_dict, {"config1.param1": 1, "config2.param2": 'config1.param1'})
    flat_dict = processing.postmerge(flat_dict, [processing])
    check.equal(flat_dict, {"config1.param1": 1, "config2.param2": 1})
    flat_dict = processing.presave(flat_dict, [processing])
    check.equal(processing.current_value, {"config2.param2": 1})
    check.equal(
        flat_dict,
        {"config1.param1": 1, "config2.param2@copy": 'config1.param1'}
    )
    check.equal(processing.keys_to_copy, {"config2.param2": "config1.param1"})
    # Reset copy processing
    processing.keys_to_copy = {}
    # Case of wrong key
    with pytest.raises(
        ValueError,
        match=(
            "Key with '@copy' tag must be associated "
            "to a string corresponding to a flat key. "
            "The problem occurs at key: a@copy with value: True"
        )
    ):
        flat_dict = processing.premerge({"a@copy": True}, [processing])
    # Case of already existing @copy but associated to an other key
    processing.keys_to_copy = {"a": "b"}
    with pytest.raises(
        ValueError,
        match=(
            "Key with '@copy' has change its value to copy. Found key: a@copy@tag "
            "with value: c, previous value to copy: b"
        )
    ):
        flat_dict = processing.premerge({"a@copy@tag": "c"}, [processing])
    # Case of non-existing key (on post-merge)
    processing.keys_to_copy = {"a": "b"}
    with pytest.raises(
        ValueError,
        match=(
            "Key to copy not found in config: b. "
            "The problem occurs with key: a"
        )
    ):
        flat_dict = processing.postmerge({"a": "b"}, [processing])
    # Case overwriting a key
    processing.current_value = {"a": 2}
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Found attempt to modify a key with '@copy' tag. The key is "
            "then protected against updates (except the copied value or "
            "the original key to copy). Found key: a of value c that copy "
            "b of value 1"
        )
    ):
        flat_dict = processing.postmerge({"a": "c", "b": 1}, [processing])


def test_process_typing() -> None:
    """Test ProcessTyping."""
    processing = ProcessTyping()
    flat_dict = {
        "param1@type:int": 1,
        "param2@type:List|Dict": [0.0],
    }
    flat_dict = processing.premerge(flat_dict, [processing])
    flat_dict['param1'] = 3
    flat_dict['param2'] = {'a': None, 'b': 1}
    flat_dict = flatten(flat_dict)
    flat_dict = processing.postmerge(flat_dict, [processing])
    check.equal(flat_dict, {"param1": 3, "param2.a": None, "param2.b": 1})
    check.equal(processing.forced_types, {"param1": (int, ), "param2": (list, dict)})
    check.equal(processing.type_desc, {"param1": "int", "param2": "List|Dict"})
    flat_dict = processing.presave(flat_dict, [processing])
    check.equal(flat_dict, {"param1@type:int": 3, "param2.a": None, "param2.b": 1})
    processing.forced_types = {}  # Reset forced types
    processing.type_desc = {}  # Reset type description

    # Case of different type on pre-merge: do not raise error!
    flat_dict = processing.premerge({"param@type:int": "str"}, [processing])

    # Case of already existing type and othere in premerge
    processing.forced_types = {"param": (int,)}
    processing.type_desc = {"param": "int"}
    with pytest.raises(
        ValueError,
        match=(
            "Find the tag '@type:str' on a key that has already been associated "
            "to an other type: int. Find problem at key: param@type:str"
        )
    ):
        flat_dict = processing.premerge({"param@type:str": "str"}, [processing])

    # Case of wrong type in postmerge
    processing.forced_types = {"param": (int,)}
    processing.type_desc = {"param": "int"}
    with pytest.raises(
        ValueError,
        match=(
            "Key previously tagged with '@type:int' must be "
            "associated to a value of type int. Find the "
            "value: mystr of type <class 'str'> at key: param"
        )
    ):
        flat_dict = processing.postmerge({"param": "mystr"}, [processing])


def test_process_check_tags() -> None:
    """Test ProcessCheckTags."""
    processing = ProcessCheckTags()
    flat_dict = {
        "config.param1": 1,
        "param1": 2,
    }
    check.equal(processing.premerge(flat_dict, [processing]), flat_dict)

    flat_dicts = [{'param1@tag': 1}, {'@foo': 2}, {'@': 3}]
    for flat_dict in flat_dicts:
        with pytest.raises(
            ValueError,
            match=(
                "Keys with tags are encountered at the end of "
                "the pre-merge process.*"
            )
        ):
            processing.premerge(flat_dict, [processing])
