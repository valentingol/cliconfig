"""Test built-in processing classes."""
import re

import pytest
import pytest_check as check

from cliconfig.base import Config
from cliconfig.dict_routines import flatten
from cliconfig.processing.builtin import (
    DefaultProcessings,
    ProcessCheckTags,
    ProcessCopy,
    ProcessDelete,
    ProcessMerge,
    ProcessNew,
    ProcessSelect,
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
    flat_config = Config(flat_dict, [processing])
    flat_config = processing.premerge(flat_config)
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
    check.equal(flat_config.dict, expected_dict)

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
        ),
    ):
        processing.premerge(Config(flat_dict, [processing]))

    # Test @merge_before and @merge_after
    flat_dict = {
        "a.b": 1,
        "a.b_path@merge_after": "tests/configs/merge/additional2.yaml",
    }
    flat_config = Config(flat_dict, [processing])
    flat_config = processing.premerge(flat_config)
    expected_dict = {
        "a.b": 2,
        "a.b_path": "tests/configs/merge/additional2.yaml",
        "c_path": "tests/configs/merge/additional3.yaml",
        "c": 3,
    }
    check.equal(flat_config.dict, expected_dict)
    flat_dict = {
        "a.b": 1,
        "a.b_path@merge_before": "tests/configs/merge/additional2.yaml",
        "c": 3,
    }
    flat_config = Config(flat_dict, [processing])
    flat_config = processing.premerge(flat_config)
    expected_dict = {
        "a.b": 1,
        "a.b_path": "tests/configs/merge/additional2.yaml",
        "c_path": "tests/configs/merge/additional3.yaml",
        "c": 3,
    }
    check.equal(flat_config.dict, expected_dict)
    check.equal(flat_config.process_list, [processing])

    # Not valid path
    for tag in ["merge_before", "merge_after", "merge_add"]:
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Key with '@{tag}' tag must be associated "
                "to a string corresponding to a *yaml* file."
                f"The problem occurs at key: a@{tag}"
            ),
        ):
            processing.premerge(Config({f"a@{tag}": "no_yaml"}, [processing]))


def test_process_copy() -> None:
    """Test ProcessCopy."""
    processing = ProcessCopy()
    flat_dict = {
        "config1.param1": 1,
        "config2.param2@copy": "config1.param1",
    }
    flat_config = Config(flat_dict, [processing])
    flat_config = processing.premerge(flat_config)
    check.equal(
        flat_config.dict, {"config1.param1": 1, "config2.param2": "config1.param1"}
    )
    flat_config.dict["config1.param1"] = 2
    flat_config = processing.postmerge(flat_config)
    check.equal(flat_config.dict, {"config1.param1": 2, "config2.param2": 2})
    check.equal(processing.copied_keys, {"config2.param2"})
    flat_config = processing.presave(flat_config)
    check.equal(processing.current_value, {"config2.param2": 2})
    check.equal(
        flat_config.dict, {"config1.param1": 2, "config2.param2@copy": "config1.param1"}
    )
    check.equal(processing.keys_to_copy, {"config2.param2": "config1.param1"})
    check.equal(flat_config.process_list, [processing])
    # Reset copy processing
    processing.keys_to_copy = {}
    # Case of wrong key
    with pytest.raises(
        ValueError,
        match=(
            "Key with '@copy' tag must be associated "
            "to a string corresponding to a flat key. "
            "The problem occurs at key: a@copy with value: True"
        ),
    ):
        processing.premerge(Config({"a@copy": True}, [processing]))
    # Case of already existing @copy but associated to an other key
    processing.keys_to_copy = {"a": "b"}
    with pytest.raises(
        ValueError,
        match=(
            "Key with '@copy' has change its value to copy. Found key: a@copy@tag "
            "with value: c, previous value to copy: b"
        ),
    ):
        processing.premerge(Config({"a@copy@tag": "c"}, [processing]))
    # Case of non-existing key (on post-merge): do not raise error
    processing.keys_to_copy = {"a": "b"}
    processing.postmerge(Config({"a": "b"}, [processing]))
    # Case of non-existing key (on end-build): raise error
    with pytest.raises(
        ValueError,
        match=re.escape(
            "A key with '@copy' tag has been found but the key to copy does not "
            "exist at the end of the build and it has been never copied. Found key: "
            "a that would copy the key: b."
        ),
    ):
        processing.endbuild(Config({"a": "b"}, [processing]))
    # Copy if it appears on end-build
    config = processing.endbuild(Config({"a": "b", "b": 3}, [processing]))
    check.equal(config.dict["a"], 3)
    # Case overwriting a key
    processing.current_value = {"a": 2}
    with pytest.raises(
        ValueError,
        match=(
            "Found attempt to modify a key with '@copy' tag. The key is "
            "protected against direct updates. Found key: a of value c that copy "
            "b of value 1"
        ),
    ):
        processing.postmerge(Config({"a": "c", "b": 1}, [processing]))


def test_process_typing() -> None:
    """Test ProcessTyping."""
    processing = ProcessTyping()
    flat_dict = {
        "param1@type:int": 1,
        "param2@type:List[Optional[Dict[str, int|float]]]": [{"a": [0.0]}],
    }
    flat_config = Config(flat_dict, [processing])
    flat_config = processing.premerge(flat_config)
    flat_config.dict["param1"] = 3
    flat_config.dict["param2"] = {"a": None, "b": [{"c": 1}]}
    flat_config.dict = flatten(flat_config.dict)
    flat_config = processing.postmerge(flat_config)
    check.equal(
        flat_config.dict, {"param1": 3, "param2.a": None, "param2.b": [{"c": 1}]}
    )
    check.equal(
        flat_config.process_list[0].forced_types,  # type: ignore
        {
            "param1": (int,),
            "param2": (("list", ((type(None), ("dict", (str,), (int, float))),)),),
        },
    )
    check.equal(
        flat_config.process_list[0].type_desc,  # type: ignore
        {"param1": "int", "param2": "List[Optional[Dict[str, int|float]]]"},
    )
    flat_config = processing.endbuild(flat_config)  # no error
    flat_config = processing.presave(flat_config)
    check.equal(
        flat_config.dict,
        {"param1@type:int": 3, "param2.a": None, "param2.b": [{"c": 1}]},
    )
    processing.forced_types = {}  # Reset forced types
    processing.type_desc = {}  # Reset type description

    # Case of different type on pre-merge: do not raise error!
    processing.premerge(Config({"param@type:int": "str"}, [processing]))

    # Case of already existing type and othere in premerge
    processing.forced_types = {"param": (int,)}
    processing.type_desc = {"param": "int"}
    with pytest.raises(
        ValueError,
        match=(
            "Find the tag '@type:str' on a key that has already been associated "
            "to an other type: int. Find problem at key: param@type:str"
        ),
    ):
        processing.premerge(Config({"param@type:str": "str"}, [processing]))

    # Case of wrong type in post-merge: no error
    processing.forced_types = {"param": (int,)}
    processing.type_desc = {"param": "int"}
    processing.postmerge(Config({"param": "mystr"}, [processing]))
    # Case of wrong type in end-build: raise error
    with pytest.raises(
        ValueError,
        match=(
            "Key previously tagged with '@type:int' must be "
            "associated to a value of type int. Find the "
            "value: mystr of type <class 'str'> at key: param"
        ),
    ):
        processing.endbuild(Config({"param": "mystr"}, [processing]))


def test_process_select() -> None:
    """Test ProcessSelect."""
    processing = ProcessSelect()
    flat_dict = {
        "models.model_names@select": ["models.model1", "models.model3"],
        "models.model1.param1": 1,
        "models.model1.param2": 2,
        "models.model2.param1": 3,
        "models.model2.param2": 4,
        "models.model3.submodel.param": 5,
        "models.model4.param": 6,
    }
    expected_dict = {
        "models.model_names": ["models.model1", "models.model3"],
        "models.model1.param1": 1,
        "models.model1.param2": 2,
        "models.model3.submodel.param": 5,
    }
    config = Config(flat_dict, [])
    config = processing.premerge(config)
    config = processing.postmerge(config)
    check.equal(config.dict, expected_dict)
    config = processing.presave(config)
    check.is_in("models.model_names@select", config.dict)
    check.equal(
        config.dict["models.model_names@select"], ["models.model1", "models.model3"]
    )
    check.is_not_in("models.model_names", config.dict)
    with pytest.raises(
        ValueError,
        match=re.escape(
            "The keys in the list of parameters tagged with '@select' must be "
            "identical before the last dot (= on the same subconfig). Find: "
            "abab and dede before the last dot."
        ),
    ):
        processing.premerge(Config({"p@select": ["abab.cdcd", "dede.fgfg"]}, []))
    with pytest.raises(
        ValueError,
        match=re.escape(
            "The value of parameters tagged with '@select' must be a string or a "
            "list of strings representing flat key(s). "
        ),
    ):
        processing.premerge(Config({"p@select": 0}, []))
    with pytest.raises(
        ValueError,
        match=(
            "Find attempt to delete the configuration at the root. You must pass a "
            "flat key with a least one dot on parameter tagged with @select. "
            "Find key: p@select with value: root"
        ),
    ):
        processing.premerge(Config({"p@select": "root"}, []))


def test_process_delete() -> None:
    """Test ProcessDelete."""
    processing = ProcessDelete()
    config = Config(
        {
            "@select@delete": "configs.config1",
            "1@merge_add@delete": "config1.yaml",
            "2@merge_add@delete": "config2.yaml",
        },
        [processing],
    )
    config = processing.premerge(config)
    check.equal(config.dict, {})


def test_process_new() -> None:
    """Test ProcessNew."""
    processing = ProcessNew()
    flat_dict = {
        "param1": 1,
        "config1": {
            "param2": 2,
            "subconfig@new": {"param3": 3, "param4": 4},
        },
        "config2@new@tag.subconfig.param3": 3,
        "config3.subconfig@new.param4": 4,
    }
    flat_dict = flatten(flat_dict)
    config = Config(flat_dict, [processing])
    check.equal(
        processing.premerge(config).dict,
        {
            "param1": 1,
            "config1.param2": 2,
        },
    )
    check.equal(
        processing.postmerge(config).dict,
        {
            "param1": 1,
            "config1.param2": 2,
            "config1.subconfig.param3": 3,
            "config1.subconfig.param4": 4,
            "config2.subconfig.param3": 3,
            "config3.subconfig.param4": 4,
        },
    )
    check.equal(
        processing.presave(config).dict,
        {
            "param1": 1,
            "config1.param2": 2,
            "config1.subconfig.param3@new": 3,
            "config1.subconfig.param4@new": 4,
            "config2.subconfig.param3@new": 3,
            "config3.subconfig.param4@new": 4,
        },
    )


def test_process_check_tags() -> None:
    """Test ProcessCheckTags."""
    processing = ProcessCheckTags()
    flat_dict = {
        "config.param1": 1,
        "param1": 2,
    }
    config = Config(flat_dict, [processing])
    check.equal(processing.premerge(config).dict, flat_dict)

    flat_dicts = [{"param1@tag": 1}, {"@foo": 2}, {"@": 3}]
    for flat_dict in flat_dicts:
        with pytest.raises(
            ValueError,
            match=(
                "Keys with tags are encountered at the end of "
                "the pre-merge process.*"
            ),
        ):
            processing.premerge(Config(flat_dict, [processing]))


def test_default_processings() -> None:
    """Test DefaultProcessings."""
    config = Config({}, DefaultProcessings().list)
    for proc in [
        ProcessCheckTags(),
        ProcessMerge(),
        ProcessCopy(),
        ProcessTyping(),
        ProcessDelete(),
        ProcessSelect(),
        ProcessNew(),
    ]:
        check.is_in(proc, config.process_list)
