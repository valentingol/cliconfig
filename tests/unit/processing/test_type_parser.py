"""Test the type parser module."""
import re

import pytest
import pytest_check as check

from cliconfig.processing._type_parser import (
    _isinstance,
    _parse_dict,
    _parse_list,
    _parse_optional,
    _parse_type,
    _parse_union,
)


def test_type_parser_isinstance() -> None:
    """Test _parse_type and _isinstance."""
    type_ = _parse_type("None")
    check.equal(type_, (type(None),))
    check.is_true(_isinstance(None, type_))
    check.is_false(_isinstance([None], type_))

    type_ = _parse_type("List[float]")
    check.equal(type_, (("list", (float,)),))

    type_ = _parse_type("list|dict")
    check.equal(type_, (list, dict))
    check.is_true(_isinstance([2.0, True], type_))

    type_ = _parse_type("Dict[str, List[float]]")
    check.equal(type_, (("dict", (str,), (("list", (float,)),)),))
    check.is_true(_isinstance({"a": [1.0, 2.0]}, type_))
    check.is_false(_isinstance({"a": [1.0, 2.0], "b": [1.0, 2]}, type_))

    type_ = _parse_type("Dict[str|bool, int|float]")
    check.equal(type_, (("dict", (str, bool), (int, float)),))

    type_ = _parse_type("Union[Optional[float], Any]")
    check.equal(type_, ((type(None), float), object))
    check.is_true(_isinstance("2", type_))

    type_ = _parse_type(
        "Dict[str, Union[List[None|float], Dict[bool, Optional[list]]]]|List[Any]|"
        "Dict[int, Optional[Dict[str, float]]]|Optional[float]"
    )
    check.equal(
        (
            (
                "dict",
                (str,),
                (
                    ("list", (type(None), float)),
                    ("dict", (bool,), ((type(None), list),)),
                ),
            ),
            ("list", (object,)),
            ("dict", (int,), ((type(None), ("dict", (str,), (float,))),)),
            (type(None), float),
        ),
        type_,
    )
    check.is_true(_isinstance({"a": [None, 1.0], "b": {True: None}}, type_))
    check.is_true(_isinstance([[]], type_))
    check.is_true(_isinstance({1: {"a": 2.0}}, type_))
    check.is_false(_isinstance({"a": [None, 1.0], "b": {False: 1, True: "1"}}, type_))

    # Wrong type description
    with pytest.raises(ValueError, match="Unknown type: 'unknown'"):
        _parse_type("unknown")
    desc = "str, List[float]"
    with pytest.raises(ValueError, match=re.escape(f"Unknown type: '{desc}'")):
        _parse_type(desc)
    desc = "None||float"
    with pytest.raises(ValueError, match=f"Unknown type: '{desc}'"):
        _parse_type(desc)
    desc = (
        "Dict[str, Union[List[None|float], Dict[bool, Optionnal[int]]]]|List[Any]|"
        "Dict[List[int], Optional[Dict[str, float]]]|float"
    )  # Optionnal with 2 n
    with pytest.raises(ValueError, match=f"Unknown type: '{desc}'"):
        _parse_type(desc)

    # Wrong type in isinstance (here a 'dict' tuple has 3 elements instead of 2)
    wrong_type = (
        (
            "dict",
            (str,),
            (
                ("list", (type(None), float)),
                ("dict", (bool,), ((type(None), list),), str),
            ),
        ),
        ("list", (object,)),
        ("dict", (int,), ((type(None), ("dict", (str,), (float,))),)),
        (type(None), float),
    )
    with pytest.raises(ValueError, match="Invalid type for _isinstance:.*"):
        _isinstance({"a": {True: "a"}}, wrong_type)


def test_errors_in_parse() -> None:
    """Test error raised in _parse_X functions."""
    with pytest.raises(ValueError, match="Invalid List type:.*"):
        _parse_list("List[bool, str]")

    with pytest.raises(ValueError, match="Invalid Dict type:.*"):
        _parse_dict("Dict[str, bool, int]]")

    with pytest.raises(ValueError, match="Invalid Union type:.*"):
        _parse_union("Union[str]")

    with pytest.raises(ValueError, match="Invalid Optional type:.*"):
        _parse_optional("Optional[str, int]")
