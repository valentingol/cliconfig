# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Private module with AST parser for safe evaluation."""
import ast
from typing import Any, Callable, Dict, List

import yaml


def _process_node(node: Any, flat_dict: dict) -> Any:
    """Compute an AST from the root by replacing param name by their values.

    The AST can contain can contain any parameter name of the configuration.
    The most usefull operators and built-in functions are supported,
    the random and math packages are also supported as well as some (safe)
    numpy, jax, tensorflow, pytorch functions. If/else statements and
    comprehension lists are also supported.
    """
    # Case None, bool or number
    if isinstance(node, ast.Constant):
        return node.n
    functions: Dict[Any, Callable[[Any, dict], Any]] = {
        ast.BinOp: _process_binop,  # binary operation
        ast.BoolOp: _process_boolop,  # boolean operation
        ast.Compare: _process_comparator,  # comparison
        ast.Name: _process_param_name,  # parameter name
        ast.Attribute: _process_subconfig,  # sub-config
        ast.IfExp: _process_ifexp,  # if/else
        ast.List: _process_ltsd,  # list
        ast.Tuple: _process_ltsd,  # tuple
        ast.Set: _process_ltsd,  # set
        ast.Dict: _process_ltsd,  # dict
        ast.Call: _process_call,  # function
        ast.ListComp: _process_lsdcomp,  # comprehension list/set/dict
        ast.SetComp: _process_lsdcomp,  # comprehension list/set/dict
        ast.DictComp: _process_lsdcomp,  # comprehension list/set/dict
        ast.comprehension: _process_comprehension,  # comprehension
    }
    if isinstance(node, tuple(functions.keys())):
        return functions[type(node)](node, flat_dict)
    raise ValueError(f"Not supported node in expression (of type {type(node)}).")


def _process_binop(node: Any, flat_dict: dict) -> Any:
    """Process a binary operator node."""
    left_val = _process_node(node=node.left, flat_dict=flat_dict)
    right_val = _process_node(node=node.right, flat_dict=flat_dict)
    operators: Dict[Any, Callable[[Any, Any], Any]] = {
        ast.Add: lambda x, y: x + y,
        ast.Sub: lambda x, y: x - y,
        ast.Mult: lambda x, y: x * y,
        ast.Div: lambda x, y: x / y,
        ast.Pow: lambda x, y: x**y,
        ast.FloorDiv: lambda x, y: x // y,
        ast.Mod: lambda x, y: x % y,
        ast.BitOr: lambda x, y: x or y,
        ast.BitAnd: lambda x, y: x and y,
        ast.MatMult: lambda x, y: x @ y,
    }
    if isinstance(node.op, tuple(operators.keys())):
        return operators[type(node.op)](left_val, right_val)
    raise ValueError(
        f"Invalid operator detected: {node.op}."
        "Please use only these ops: '+', '-', '*', '/', '**', "
        "'//', '%', '|', '&'."
    )


def _process_boolop(node: Any, flat_dict: dict) -> Any:
    """Process bool operator node."""
    values = [
        _process_node(node=nodeval, flat_dict=flat_dict) for nodeval in node.values
    ]
    operators: Dict[Any, Callable[[Any, Any], Any]] = {
        ast.And: lambda x, y: x and y,
        ast.Or: lambda x, y: x or y,
    }
    operator = operators[type(node.op)]
    result = isinstance(node.op, ast.And)  # Neutral for the operation
    for val in values:
        result = operator(result, val)  # type: ignore
    return result


def _process_comparator(node: Any, flat_dict: dict) -> Any:
    """Process a comparator node."""
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


def _process_param_name(node: Any, flat_dict: dict) -> Any:
    """Process a parameter name."""
    name = node.id
    if name in flat_dict:
        if isinstance(flat_dict[name], (bool, int, float, complex, list, type(None))):
            return flat_dict[name]
        raise ValueError(
            f"Invalid value in expression for parameter '{name}', "
            f"found type {type(flat_dict[name])}, expected, None, bool, int, "
            "float, complex or list."
        )
    raise ValueError(f"Unknown parameter '{name}'.")


def _process_subconfig(node: Any, flat_dict: dict) -> Any:
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


def _process_ifexp(node: Any, flat_dict: dict) -> Any:
    """Process a if/exp statement."""
    test_val = _process_node(node=node.test, flat_dict=flat_dict)
    return (
        _process_node(node=node.body, flat_dict=flat_dict)
        if test_val
        else _process_node(node=node.orelse, flat_dict=flat_dict)
    )


def _process_ltsd(node: Any, flat_dict: dict) -> Any:
    """Process a list, a tuple, a set or a dict node."""
    if isinstance(node, ast.List):
        # List
        return [
            _process_node(node=element, flat_dict=flat_dict) for element in node.elts
        ]
    if isinstance(node, ast.Tuple):
        # Tuple
        return tuple(
            _process_node(node=element, flat_dict=flat_dict) for element in node.elts
        )
    if isinstance(node, ast.Set):
        # Set
        return {
            _process_node(node=element, flat_dict=flat_dict) for element in node.elts
        }
    # Dict
    return {
        _process_node(node=key, flat_dict=flat_dict): _process_node(
            node=value, flat_dict=flat_dict
        )
        for (key, value) in zip(node.keys, node.values)
    }


def _process_call(node: Any, flat_dict: dict) -> Any:
    """Process a function node."""
    functions: Dict[str, Callable] = {
        "len": len,
        "sum": sum,
        "max": max,
        "min": min,
        "abs": abs,
        "round": round,
        "all": all,
        "any": any,
        "range": range,
        "bool": bool,
        "int": int,
        "float": float,
        "str": str,
        "list": list,
        "tuple": tuple,
        "dict": dict,
        "set": set,
    }
    args = [_process_node(node=arg, flat_dict=flat_dict) for arg in node.args]
    kwargs = {
        kwarg.arg: _process_node(node=kwarg.value, flat_dict=flat_dict)
        for kwarg in node.keywords
    }
    if isinstance(node.func, ast.Name):
        func_name = node.func.id
        value = functions[func_name](*args, **kwargs)
        return value

    # ast.Attribute
    func = _find_function(node=node.func, flat_dict=flat_dict)
    return func(*args, **kwargs)


def _find_function(node: Any, flat_dict: dict) -> Callable:
    """Find a function from node."""
    list_names: List[str] = []
    while isinstance(node, ast.Attribute):
        list_names = [str(node.attr)] + list_names
        node = node.value
    list_names = [node.id] + list_names

    aliases = {"np": "numpy", "tf": "tensorflow"}
    if list_names[0] in aliases:
        list_names[0] = aliases[list_names[0]]
    list_names = (
        ["jax", "numpy"] + list_names[1:] if list_names[0] == "jnp" else list_names
    )

    if list_names[0] in flat_dict:
        obj = flat_dict[list_names[0]]
    elif _filter_allowed(list_names=list_names):
        obj = __import__(list_names[0])
    else:
        raise ValueError(
            f"Package or function not allowed or not supported: {'.'.join(list_names)}"
        )
    for name in list_names[1:-1]:
        obj = getattr(obj, name)
    func = getattr(obj, list_names[-1])
    return func


def _filter_allowed(list_names: List[str]) -> bool:
    """Filter the allowed functions."""
    with open(
        "cliconfig/processing/allowed_functions.yaml", encoding="utf-8"
    ) as yaml_file:
        allowed_funcs = yaml.safe_load(yaml_file)
    list_names = list_names.copy()
    # jax and numpy share the same allowed functions, jax.random is also allowed
    list_names = list_names[1:] if list_names[0] == "jax" else list_names

    if any(name.startswith("_") for name in list_names):
        return False
    if list_names[0] in ("random", "math"):
        return True
    if list_names[0] in ("numpy", "torch", "tensorflow"):
        return list_names[1] in allowed_funcs[list_names[0]]
    return False


def _process_lsdcomp(node: Any, flat_dict: dict) -> Any:
    """Process comprehension list, set or dict node."""
    generator = node.generators[0]
    if isinstance(node, (ast.ListComp, ast.SetComp)):
        elt = node.elt
        result = []
        for variables in _process_node(generator, flat_dict=flat_dict):
            result.append(_process_node(elt, flat_dict=variables))
        return result if isinstance(node, ast.ListComp) else set(result)
    # DictComp
    dict_result: Dict = {}
    for variables in _process_node(generator, flat_dict=flat_dict):
        key = _process_node(node.key, flat_dict=variables)
        value = _process_node(node.value, flat_dict=variables)
        dict_result[key] = value
    return dict_result


def _process_comprehension(node: Any, flat_dict: dict) -> Any:
    """Process comprehension node."""
    target = node.target
    iterator = node.iter
    tests = node.ifs
    if isinstance(target, ast.Tuple):
        target = tuple(elt for elt in target.elts)

    variables = flat_dict.copy()
    for val in _process_node(node=iterator, flat_dict=flat_dict):
        if isinstance(target, tuple):
            variables.update({target.id: val[i] for i, target in enumerate(target)})
        else:
            variables[target.id] = val
        condition = all(_process_node(test, variables) for test in tests)
        if condition:
            yield variables
