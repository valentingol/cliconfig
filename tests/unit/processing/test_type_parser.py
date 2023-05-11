"""Test the type parser module."""
import re

import pytest
import pytest_check as check

from cliconfig.processing._type_parser import _parse_type


def test_type_parser() -> None:
    """Test _parse_type."""
    check.equal(_parse_type("None"), {type(None)})
    check.equal(_parse_type("Dict[str, List[float]]"), {dict})
    check.equal(_parse_type("Union[Optional[float], Any]"), {float, type(None), object})
    check.equal(
        _parse_type(
            "Dict[str, Union[List[None|float], Dict[bool, Optional[int]]]]|List[Any]|"
            "Dict[List[int], Optional[Dict[str, float]]]|Optional[float]"
        ),
        {type(None), dict, list, float}
    )
    with pytest.raises(ValueError, match="Unknown type: 'unknown'"):
        _parse_type("unknown")
    desc = "str, List[float]"
    with pytest.raises(ValueError, match=re.escape(f"Unknown type: '{desc}'")):
        _parse_type(desc)
    desc = ("None||float")
    with pytest.raises(ValueError, match=f"Unknown type: '{desc}'"):
        _parse_type(desc)
    desc = ("Dict[str, Union[List[None|float], Dict[bool, Optional[int]]]]|List[Any]|"
            "Dict[List[int], Optional[Dict[str, float]]]|flsoat")  # flsoat != float
    with pytest.raises(ValueError, match=f"Unknown type: '{desc}'"):
        _parse_type(desc)
