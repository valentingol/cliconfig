"""Private module with type parser for processing module with type manipulation."""
import ast
from typing import Any, Callable, Dict, Union

ValType = Union[int, float, complex, bool]


def _process_node(node: Any, flat_dict: dict) -> ValType:
    """Compute an AST from the root by replacing param name by their values.

    The AST should only contain bool, numbers (int, float, complex),
    parenthesis, parameter names and following operators:
    +, -, *, /, **, //, %, |, &
    Also support comparison operators: <, <=, ==, !=, ... and if/else.
    """
    # Case bool or number
    if isinstance(node, ast.Constant):
        return node.n
    functions: Dict[Any, Callable[[Any, dict], ValType]] = {
        ast.BinOp: _process_binop,  # binary operation
        ast.Compare: _process_comparator,  # comparison
        ast.Name: _process_param_name,  # parameter name
        ast.Attribute: _process_subconfig,  # sub-config
        ast.IfExp: _process_ifexp,  # if/else
    }
    if isinstance(node, tuple(functions.keys())):
        return functions[type(node)](node, flat_dict)
    raise ValueError(f"Invalid node in expression (of type {type(node)}).")


def _process_binop(node: Any, flat_dict: dict) -> ValType:
    """Process a binary operation."""
    left_val = _process_node(node=node.left, flat_dict=flat_dict)
    right_val = _process_node(node=node.right, flat_dict=flat_dict)
    operators: Dict[Any, Callable[[ValType, ValType], ValType]] = {
        ast.Add: lambda x, y: x + y,
        ast.Sub: lambda x, y: x - y,
        ast.Mult: lambda x, y: x * y,
        ast.Div: lambda x, y: x / y,
        ast.Pow: lambda x, y: x**y,
        ast.FloorDiv: lambda x, y: x // y,  # type: ignore
        ast.Mod: lambda x, y: x % y,  # type: ignore
        ast.BitOr: lambda x, y: x or y,
        ast.BitAnd: lambda x, y: x and y,
    }
    if isinstance(node.op, tuple(operators.keys())):
        return operators[type(node.op)](left_val, right_val)
    raise ValueError(
        f"Invalid operator detected: {node.op}."
        "Please use only these ops: '+', '-', '*', '/', '**', "
        "'//', '%', '|', '&'."
    )


def _process_comparator(node: Any, flat_dict: dict) -> ValType:
    """Process a comparator operation."""
    left_val = _process_node(node=node.left, flat_dict=flat_dict)
    right_val = _process_node(node=node.comparators[0], flat_dict=flat_dict)
    operators: Dict[Any, Callable[[bool, bool], bool]] = {
        ast.Eq: lambda x, y: x == y,
        ast.NotEq: lambda x, y: x != y,
        ast.Lt: lambda x, y: x < y,
        ast.LtE: lambda x, y: x <= y,
        ast.Gt: lambda x, y: x > y,
        ast.GtE: lambda x, y: x >= y,
    }
    return operators[type(node.ops[0])](left_val, right_val)  # type: ignore


def _process_param_name(node: Any, flat_dict: dict) -> ValType:
    """Process a parameter name."""
    name = node.id
    if name in flat_dict:
        if isinstance(flat_dict[name], (bool, int, float, complex)):
            return flat_dict[name]
        raise ValueError(
            f"Invalid value in expression for parameter '{name}', "
            f"found type {type(flat_dict[name])}, expected, int, "
            "float or complex."
        )
    raise ValueError(f"Unknown parameter '{name}'.")


def _process_subconfig(node: Any, flat_dict: dict) -> ValType:
    """Process a sub-config."""
    # Get recursively the attribute names
    param_name = ""
    while isinstance(node, ast.Attribute):
        param_name = f"{node.attr}.{param_name}"
        node = node.value
    # Add the global subconfig name and process the node containing the
    # full flat parameter name
    param_name = f"{node.id}.{param_name}"[:-1]  # Remove last dot
    node = ast.Name(id=param_name, ctx=ast.Load())
    return _process_node(node=node, flat_dict=flat_dict)


def _process_ifexp(node: Any, flat_dict: dict) -> ValType:
    """Process a sub-config."""
    # Get recursively the attribute names
    test_val = _process_node(node=node.test, flat_dict=flat_dict)
    return (
        _process_node(node=node.body, flat_dict=flat_dict)
        if test_val
        else _process_node(node=node.orelse, flat_dict=flat_dict)
    )
