"""Test helpers to create processing functions."""
import re

import pytest
import pytest_check as check

from cliconfig.processing.create import create_processing_value


def test_create_processing_value() -> None:
    """Test create_processing_value."""
    # Persistent
    proc2 = create_processing_value(lambda x: -x, regex="neg_number.*", order=0.0)
    proc1 = create_processing_value(lambda x: x + 1, tag_name="add1", order=1.0,
                                    persistent=True)
    in_dict = {"neg_number1": 1, "neg_number2": 1, "neg_number3@add1": 1}
    in_dict = proc2.premerge(in_dict, [proc1, proc2])
    in_dict = proc1.premerge(in_dict, [proc1, proc2])
    check.equal(in_dict, {"neg_number1": -1, "neg_number2": -1, "neg_number3": 0})
    in_dict = proc2.premerge(in_dict, [proc1, proc2])
    in_dict = proc1.premerge(in_dict, [proc1, proc2])
    check.equal(in_dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 1})
    # Non persistent
    proc2 = create_processing_value(lambda x: -x, regex="neg_number.*", order=0.0)
    proc1 = create_processing_value(lambda x: x + 1, tag_name="add1", order=1.0,
                                    persistent=False)
    in_dict = {"neg_number1": 1, "neg_number2": 1, "neg_number3@add1": 1}
    in_dict = proc2.premerge(in_dict, [proc1, proc2])
    in_dict = proc1.premerge(in_dict, [proc1, proc2])
    check.equal(in_dict, {"neg_number1": -1, "neg_number2": -1, "neg_number3": 0})
    in_dict = proc2.premerge(in_dict, [proc1, proc2])
    in_dict = proc1.premerge(in_dict, [proc1, proc2])
    check.equal(in_dict, {"neg_number1": 1, "neg_number2": 1, "neg_number3": 0})

    # Failing cases
    with pytest.raises(
        ValueError,
        match="You must provide a tag or a regex but not both."
    ):
        create_processing_value(lambda x: x + 1, tag_name="add1", regex="neg_number.*")
    with pytest.raises(
        ValueError,
        match=re.escape("You must provide a tag or a regex "
                        "(to trigger the value update).")
    ):
        create_processing_value(lambda x: x + 1, order=0.0)
