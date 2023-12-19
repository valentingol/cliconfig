# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Test the AST parser module."""
import ast
import re

import numpy as np
import pytest
import pytest_check as check

from cliconfig.processing._ast_parser import _process_node


def test_ast_parser() -> None:
    """Test the AST parser module."""
    flat_dict: dict = {"cfg1.cfg2.cfg3.param1": 4.2, "param2": 6.2}
    expr = "(1 + 2 * cfg1.cfg2.cfg3.param1 + (param2 // 2) ** 2 - 3 / 4) % 10"
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.almost_equal(result, 7.65)

    flat_dict = {"param1": 0.2, "param2": False}
    expr = (
        "tuple([param1 if (param1 > 0.1) and (param1 <= 0.2) & "
        "(param1 == 0.2) and (param2 | True) else 0] * 2)"
    )
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.equal(result, (0.2, 0.2))

    expr = "sum([1 for _ in range(2)])"
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.equal(result, 2)

    flat_dict = {"elems": [(1, 2), (3, 4), (5, 6)], "val": 2}
    expr = "{'list': [i+2*j for i, j in elems if i > val]}, val"
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.equal(result, ({"list": [11, 17]}, 2))

    flat_dict = {"a": {"b": 1}}
    expr = "list(a.keys())"
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.equal(result, ["b"])

    flat_dict = {"elems": [1, 2, 3], "val": 5}
    expr = "np.array(elems + [random.randint(0, val)]), np.random.randint(0, 5)"
    tree = ast.parse(expr, mode="eval")
    result = _process_node(node=tree.body, flat_dict=flat_dict)
    check.is_instance(result[0], np.ndarray)
    check.is_true(0 <= result[1] < 5)
    check.is_true(np.allclose(result[0][:3], [1, 2, 3]))

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
    tree = ast.parse("lambda x: 0", mode="eval")
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Not supported node in expression (of type <class 'ast.Lambda'>)."
        ),
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

    # Case invalid package or function
    tree = ast.parse("np.save('tmp.npy', np.array([1, 2, 3]))", mode="eval")
    with pytest.raises(
        ValueError,
        match="Package or function not allowed or not supported: numpy.save",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)

    tree = ast.parse("random._exp()", mode="eval")
    with pytest.raises(
        ValueError,
        match="Package or function not allowed or not supported: random._exp",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)
    tree = ast.parse("logml.Logger()", mode="eval")
    with pytest.raises(
        ValueError,
        match="Package or function not allowed or not supported: logml.Logger",
    ):
        _process_node(node=tree.body, flat_dict=flat_dict)
