"""Test helpers to create processing functions."""
import re

import pytest
import pytest_check as check

from cliconfig.base import Config
from cliconfig.processing.create import (
    _is_matched,
    create_processing_keep_property,
    create_processing_value,
)


def test_is_matched() -> None:
    """Test _is_matched."""
    check.is_true(_is_matched("foo.bar.test", regex=".*st", tag_name=None))
    check.is_false(_is_matched("test.bar.foo", regex=".*st", tag_name=None))
    check.is_true(_is_matched("foo.bar.test@tag", regex=None, tag_name="tag"))
    check.is_false(_is_matched("foo.bar@tag.test", regex=None, tag_name="tag"))
    check.is_false(_is_matched("foo.bar.test@tag2", regex=None, tag_name="tag"))
    with pytest.raises(
        ValueError, match="Either regex or tag_name must be defined but not both."
    ):
        _is_matched("foo.bar", ".*", "tag")
    with pytest.raises(ValueError, match="Either regex or tag_name must be defined."):
        _is_matched("foo.bar", None, None)


def test_create_processing_value() -> None:
    """Test create_processing_value."""
    # Persistent, premerge
    proc1 = create_processing_value(
        lambda x: x + 1, tag_name="add1", order=1.0, persistent=True
    )
    proc2 = create_processing_value(
        lambda x: -x, regex="neg_number.*", order=0.0, persistent=True
    )
    in_dict = {"neg_number1": 1, "neg_number2": 1, "neg_number3@add1": 1}
    config = Config(in_dict, [proc1, proc2])
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    check.equal(config.dict, {"neg_number1": -1, "neg_number2": -1, "neg_number3": 0})
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    config = config.process_list[1].postmerge(config)
    config = config.process_list[0].postmerge(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    config = config.process_list[1].endbuild(config)
    config = config.process_list[0].endbuild(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    config = config.process_list[1].presave(config)
    config = config.process_list[0].presave(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    config = config.process_list[1].postload(config)
    config = config.process_list[0].postload(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    # Non persistent, postmerge
    proc2 = create_processing_value(
        lambda x: -x, "postmerge", regex="neg_number.*", order=0.0, persistent=False
    )
    proc1 = create_processing_value(
        lambda x: x + 1, "postmerge", tag_name="add1", order=1.0, persistent=False
    )
    in_dict = {"neg_number1": 1, "neg_number2": 1, "neg_number3@add1": 1}
    config = Config(in_dict, [proc1, proc2])
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    config = config.process_list[1].postmerge(config)
    config = config.process_list[0].postmerge(config)
    check.equal(config.dict, {"neg_number1": -1, "neg_number2": -1, "neg_number3": 0})
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    config = config.process_list[1].postmerge(config)
    config = config.process_list[0].postmerge(config)
    check.equal(config.dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 0})
    # No signature, endbuild, presave, postload
    proc1 = create_processing_value(type, "endbuild", tag_name="get_type")
    proc2 = create_processing_value(str, "presave", tag_name="to_str")
    proc3 = create_processing_value(
        lambda *args: 0, "postload", tag_name="zero"  # noqa
    )
    in_dict2 = {
        "type1@get_type@to_str@zero": 1,
        "type2@get_type@to_str@zero": "2",
        "type3@get_type@to_str@zero": True,
    }
    config = Config(in_dict2, [proc1, proc2, proc3])
    config = config.process_list[0].premerge(config)
    config = config.process_list[1].premerge(config)
    config = config.process_list[2].premerge(config)
    check.equal(config.dict, {"type1": 1, "type2": "2", "type3": True})
    config = config.process_list[0].endbuild(config)
    check.equal(config.dict, {"type1": int, "type2": str, "type3": bool})
    config = config.process_list[1].presave(config)
    check.equal(
        config.dict,
        {"type1": "<class 'int'>", "type2": "<class 'str'>", "type3": "<class 'bool'>"},
    )
    config = config.process_list[2].postload(config)
    check.equal(config.dict, {"type1": 0, "type2": 0, "type3": 0})

    # Config in input
    proc = create_processing_value(
        lambda x, flat_config: eval(  # pylint: disable=eval-used
            x, {"config": flat_config}
        ),
        tag_name="eval",
        persistent=False,
    )
    eval_dict = {"param1": 1, "param2@eval": "config.param1 + 1"}
    config = Config(eval_dict, [proc])
    config = config.process_list[0].premerge(config)
    check.equal(config.dict, {"param1": 1, "param2": 2})

    # Failing cases
    with pytest.raises(ValueError, match="Processing type 'UNKNOWN' not recognized.*"):
        create_processing_value(lambda x: x + 1, "UNKNOWN", tag_name="tag")
    with pytest.raises(
        ValueError, match="You must provide a tag or a regex but not both."
    ):
        create_processing_value(lambda x: x + 1, tag_name="add1", regex="neg_number.*")
    with pytest.raises(
        ValueError,
        match=re.escape(
            "You must provide a tag or a regex (to trigger the value update)."
        ),
    ):
        create_processing_value(lambda x: x + 1, order=0.0)

    # Test repr
    def add1(x: int) -> int:
        """Add 1."""
        return x + 1

    proc = create_processing_value(add1, tag_name="add1", order=1.0, persistent=True)
    check.equal(
        repr(proc),
        (
            "ProcessingValue(func=add1, tag=add1, regex=None, "
            "type=premerge, persistent=True, order=1.0)"
        ),
    )


def test_create_processing_keep_property() -> None:
    """Test create_processing_keep_property."""
    proc1 = create_processing_keep_property(type, regex=".*")
    proc2 = create_processing_keep_property(lambda x: x, tag_name="protect")
    proc3 = create_processing_keep_property(
        lambda x, config: len(x + config.dict["list"]),
        tag_name="len",
    )
    in_dict = {"str": "foo", "int": 2, "list@protect": [1, 2, 3], "list2@len": [1, 2]}
    config = Config(in_dict, [proc1, proc2, proc3])
    config = config.process_list[0].premerge(config)
    config = config.process_list[1].premerge(config)
    config = config.process_list[2].premerge(config)
    check.equal(
        config.dict, {"str": "foo", "int": 2, "list": [1, 2, 3], "list2": [1, 2]}
    )
    config.dict = {"str": "foo", "int": -1, "list": [1, 2, 3], "list2": [4, 5]}
    config = config.process_list[0].postmerge(config)
    config = config.process_list[1].postmerge(config)
    config = config.process_list[2].postmerge(config)
    config.dict = {"str": "foo2", "int": 6, "list": [1, 2, 3], "list2": [8, 9]}
    config = config.process_list[0].endbuild(config)
    config = config.process_list[1].endbuild(config)
    config = config.process_list[2].endbuild(config)
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Property of key str has changed from <class 'str'> to <class 'int'> "
            "while it is protected by a keep-property processing (problem found on "
            "end-build)."
        ),
    ):
        config.process_list[0].endbuild(Config({"str": 0}, []))
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Property of key list has changed from [1, 2, 3] to [1, 2] while "
            "it is protected by a keep-property processing (problem found on "
            "post-merge)."
        ),
    ):
        config.process_list[1].postmerge(Config({"list": [1, 2]}, []))
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Property of key list2 has changed from 5 to 3 while "
            "it is protected by a keep-property processing (problem found on "
            "post-merge)."
        ),
    ):
        config.process_list[2].postmerge(Config({"list": [1, 2], "list2": [3]}, []))
    # Should not raise on pre-merge:
    config.process_list[0].premerge(Config({"str": 0}, []))
    config.process_list[1].premerge(Config({"list": [1, 2]}, []))
    config.process_list[2].premerge(Config({"list": [1, 2], "list2": []}, []))

    # Failing cases
    with pytest.raises(
        ValueError, match="You must provide a tag or a regex but not both."
    ):
        create_processing_keep_property(lambda x: x, tag_name="protect", regex=".*")
    with pytest.raises(
        ValueError,
        match=re.escape(
            "You must provide a tag or a regex (to trigger the value update)."
        ),
    ):
        create_processing_keep_property(lambda x: x, premerge_order=0.0)

    # Test repr
    proc = create_processing_keep_property(sum, tag_name="keep_sum", endbuild_order=1.0)
    check.equal(
        repr(proc),
        (
            "ProcessingKeepProperty(func=sum, tag=keep_sum, regex=None, "
            "orders=(0.0, 0.0, 1.0))"
        ),
    )
