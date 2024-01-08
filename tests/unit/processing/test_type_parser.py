# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Test the type parser module."""
import re

import pytest
import pytest_check as check

from cliconfig.processing._type_parser import (
    _convert_type,
    _isinstance,
    _parse_dict,
    _parse_optional,
    _parse_set_list,
    _parse_type,
    _parse_union,
)


def test_type_routines() -> None:
    """Test _parse_type, _isinstance and _convert_type."""
    type_ = _parse_type("None")
    check.equal(type_, (type(None),))
    check.is_true(_isinstance(None, type_))
    check.is_false(_isinstance([None], type_))
    check.equal(_convert_type("unchanged", type_), "unchanged")

    check.is_true(_isinstance(obj=False,  types=_parse_type("bool")))
    check.is_true(_isinstance(2.3,  _parse_type("float")))
    check.is_true(_isinstance((1, 2),  _parse_type("tuple")))
    check.is_true(_isinstance({1, 2},  _parse_type("set")))
    check.equal(a=_convert_type(0,  _parse_type("bool")), b=False)
    check.equal(_convert_type(2.3,  _parse_type("int")), 2)
    check.equal(_convert_type([[1, 2]], _parse_type("dict")), {1: 2})
    check.equal(_convert_type([1, 2], _parse_type("tuple")), (1, 2))
    check.equal(_convert_type((1, 1), _parse_type("set")), {1})

    type_ = _parse_type("List[float]")
    check.equal(type_, (("list", (float,)),))

    type_ = _parse_type("dict|list")
    check.equal(type_, (dict, list))
    check.is_true(_isinstance([2.0, True], type_))
    check.equal(_convert_type((0, 1), type_), [0, 1])

    type_ = _parse_type("Dict[str, List[float]]")
    check.equal(type_, (("dict", (str,), (("list", (float,)),)),))
    check.is_true(_isinstance({"a": [1.0, 2.0]}, type_))
    check.is_false(_isinstance({"a": [1.0, 2.0], "b": [1.0, 2]}, type_))
    check.equal(
        _convert_type({"a": [1.0, 2.0], "b": [1.0, 2]}, type_),
        {"a": [1.0, 2.0], "b": [1.0, 2.0]},
    )

    type_ = _parse_type("Dict[str|bool, int|float]")
    check.equal(type_, (("dict", (str, bool), (int, float)),))

    type_ = _parse_type("Dict[str, Set[float]]")
    check.equal(type_, (("dict", (str,), (("set", (float,)),)),))
    check.is_true(_isinstance({"a": {1.0, 2.0}}, type_))
    check.equal(
        _convert_type({"a": [1.0, 2.0], "b": [1.0, 2]}, type_),
        {"a": {1.0, 2.0}, "b": {1.0, 2.0}},
    )

    type_ = _parse_type("Dict[str, Tuple[float, str]]")
    check.equal(type_, (("dict", (str,), (("tuple", (float,), (str,)),)),))
    check.is_true(_isinstance({"a": (0.2, "a")}, type_))
    check.is_false(_isinstance({"a": [0.2, "a"]}, type_))
    check.is_false(_isinstance({"a": [2, "a"]}, type_))
    check.equal(
        _convert_type({"a": {1, 2}, "b": [1, 2]}, type_),
        {"a": (1.0, "2"), "b": (1, "2")},
    )

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

    type_ = _parse_type("Dict[int, Optional[Dict[str, float]]]")
    check.equal(
        _convert_type({"0": {1: True, 2: "2.3"}, "1": {3: 3, 4: 4}}, type_),
        {0: {"1": 1.0, "2": 2.3}, 1: {"3": 3.0, "4": 4.0}},
    )
    check.equal(_convert_type({"str": None}, type_), {"str": None})

    # Wrong type description
    check.equal(_convert_type({"str": None}, ("list")), {"str": None})  # type: ignore
    with pytest.raises(ValueError, match="Unknown type: 'unknown'"):
        _parse_type("unknown")
    desc = "str, List[float]"
    with pytest.raises(ValueError, match=re.escape(f"Unknown type: '{desc}'")):
        _parse_type(desc)
    desc = "None||float"
    with pytest.raises(ValueError, match=f"Unknown type: '{desc}'"):
        _parse_type(desc)
    desc = "Unknown[float]"
    with pytest.raises(ValueError, match=re.escape(f"Unknown type: '{desc}'")):
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
        _parse_set_list("list", "List[bool, str]")

    with pytest.raises(ValueError, match="Invalid Dict type:.*"):
        _parse_dict("Dict[str, bool, int]]")

    with pytest.raises(ValueError, match="Invalid Union type:.*"):
        _parse_union("Union[str]")

    with pytest.raises(ValueError, match="Invalid Optional type:.*"):
        _parse_optional("Optional[str, int]")
