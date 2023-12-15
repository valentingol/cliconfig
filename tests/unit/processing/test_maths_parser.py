"""Test the type parser module."""
import ast
import re

import pytest
import pytest_check as check

from cliconfig.processing._maths_parser import _process_node


def test_maths_parser() -> None:
    """Test the maths parser module."""
    flat_dict = {"cfg1.cfg2.cfg3.param1": 4.2, "param2": 6.2}
    expr = "(1 + 2 * cfg1.cfg2.cfg3.param1 + (param2 // 2) ** 2 - 3 / 4) % 10"
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.almost_equal(result, 7.65)

    flat_dict = {"param1": 0.2, "param2": False}
    expr = (
        "param1 if (param1 > 0.1) & (param1 <= 0.2) & "
        "(param1 == 0.2) & (param2 | True) else 0"
    )
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.equal(result, 0.2)

    # Case not valid parameter value
    flat_dict = {"param1": 2, "param2": "string"}  # type: ignore
    tree = ast.parse("param1 + param2", mode="eval")
    with pytest.raises(
        ValueError,
        match="Invalid value in expression for parameter 'param2'.*",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)

    # Case unknown parameter
    tree = ast.parse("param1 + unknown", mode="eval")
    with pytest.raises(
        ValueError,
        match="Unknown parameter 'unknown'.",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)

    # Case invalid node
    tree = ast.parse("param1 and True", mode="eval")
    with pytest.raises(
        ValueError,
        match=re.escape("Invalid node in expression (of type <class 'ast.BoolOp'>)."),
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)

    # Case invalid binary operator
    tree = ast.parse("param1 >> param1", mode="eval")
    with pytest.raises(
        ValueError,
        match="Invalid operator detected: <ast.RShift.*",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)

    # Case invalid compare operator
    tree = ast.parse("param1 >> param1", mode="eval")
    with pytest.raises(
        ValueError,
        match="Invalid operator detected: <ast.RShift.*",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)
