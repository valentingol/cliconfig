"""Test helpers to create processing functions."""
import re

import pytest
import pytest_check as check

from cliconfig.base import Config
from cliconfig.processing.create import (
    create_processing_keep_property,
    create_processing_value,
)


def test_create_processing_value() -> None:
    """Test create_processing_value."""
    # Persistent
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
    check.equal(in_dict, {"neg_number1": -1, "neg_number2": -1, "neg_number3": 0})
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    check.equal(in_dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    # Non persistent
    proc2 = create_processing_value(
        lambda x: -x, regex="neg_number.*", order=0.0, persistent=False
    )
    proc1 = create_processing_value(
        lambda x: x + 1, tag_name="add1", order=1.0, persistent=False
    )
    in_dict = {"neg_number1": 1, "neg_number2": 1, "neg_number3@add1": 1}
    config = Config(in_dict, [proc1, proc2])
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    check.equal(in_dict, {"neg_number1": -1, "neg_number2": -1, "neg_number3": 0})
    config = config.process_list[1].premerge(config)
    config = config.process_list[0].premerge(config)
    check.equal(in_dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 0})

    # Failing cases
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


def test_create_processing_keep_property() -> None:
    """Test create_processing_keep_property."""
    proc1 = create_processing_keep_property(type, regex=".*")
    proc2 = create_processing_keep_property(lambda x: x, tag_name="protect")
    in_dict = {"str": "foo", "int": 2, "list@protect": [1, 2, 3]}
    config = Config(in_dict, [proc1, proc2])
    config = config.process_list[0].premerge(config)
    config = config.process_list[1].premerge(config)
    check.equal(config.dict, {"str": "foo", "int": 2, "list": [1, 2, 3]})
    config = config.process_list[0].postmerge(config)
    config = config.process_list[1].postmerge(config)
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Property of key str has changed from <class 'str'> to <class 'int'> "
            "while it is protected by a keep-property processing (problem found on "
            "post-merge)."
        ),
    ):
        config.process_list[0].postmerge(Config({"str": 0}, []))
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Property of key list has changed from [1, 2, 3] to [1, 2] while "
            "it is protected by a keep-property processing (problem found on "
            "post-merge)."
        ),
    ):
        config.process_list[1].postmerge(Config({"list": [1, 2]}, []))
    config.process_list[0].premerge(Config({"str": 0}, []))  # should not raise
    config.process_list[1].premerge(Config({"list": [1, 2]}, []))  # should not raise

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
