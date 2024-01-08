# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Private module with type parser for processing module with type manipulation."""
from functools import partial
from pydoc import locate
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union


def _parse_type(type_desc: str) -> Tuple:
    """Parse a type description.

    Allow basic types (none, any, bool, int, float, str, list, set, tuple, dict),
    nested lists/sets/dicts, unions (with Union or the '|' symbol) and Optional.

    Examples of representation:
    * "str" -> (str,)
    * "None|Any" -> (type(None), object)
    * "list|float" -> (list, float)
    * "List[float]" -> (("list", (float,)),)
    * "Dict[str, Any]" -> (("dict", (str,), (object,)),)
    * "Dict[str, List[float]]" -> (("dict", (str,), ((("list", (float,)),),)),)
    * "Dict[str|bool, int|float]" -> (("dict", (str, bool), (int, float)),)
    * ...

    Raises
    ------
    ValueError
        If the type description is not valid or not recognized.

    Notes
    -----
    The type description is lowercased and spaces are removed before parsing.
    """
    # Clean up
    old_type_desc = type_desc
    type_desc = type_desc.replace(" ", "").lower()
    try:
        # Base typeParseType
        base_type = _parse_base_type(type_desc)
        if base_type is not None:
            return (base_type,)
        # Split the external blocks enclosed by brackets
        blocks = _split_brackets(type_desc, delimiter="|")
        types: Tuple = ()
        for block in blocks:
            if "[" in block:
                kind = block[: block.index("[")]
                parsing_funcs: Dict[str, Callable] = {
                    "list": partial(_parse_set_list, kind="list"),
                    "set": partial(_parse_set_list, kind="set"),
                    "dict": _parse_dict,
                    "tuple": _parse_tuple,
                    "optional": _parse_optional,
                    "union": _parse_union,
                }
                if kind not in parsing_funcs:
                    raise ValueError(f"Unknown type: '{block}'")
                types += parsing_funcs[kind](type_desc=block)
            else:  # Should be a base type
                base_type = _parse_base_type(type_desc=block)
                if base_type is not None:
                    types += (base_type,)
                else:
                    raise ValueError(f"Unknown type: '{block}'")
        return types
    except ValueError as err:
        # Revert the traceback to show the original type description
        raise ValueError(f"Unknown type: '{old_type_desc}'") from err


def _parse_base_type(type_desc: str) -> Optional[Type]:
    """Parse a base type description.

    Base types are: none, any, bool, int, float and str, list, dict.
    Return None if the type is not a base type.
    """
    if type_desc == "none":
        return type(None)
    if type_desc == "any":
        # Match any type
        return object
    if type_desc in ("bool", "int", "float", "str", "list", "set", "tuple", "dict"):
        return locate(type_desc)  # type: ignore
    return None


def _parse_set_list(kind: str, type_desc: str) -> Tuple:
    """Parse a "list" or a "set" type description."""
    sub_desc = type_desc[5:-1] if kind == "list" else type_desc[4:-1]
    if len(_split_brackets(sub_desc, delimiter=",")) > 1:
        raise ValueError(f"Invalid {kind.capitalize()} type: '{type_desc}'")
    return ((kind,) + (_parse_type(sub_desc),),)


def _parse_dict(type_desc: str) -> Tuple:
    """Parse an "dict" type description."""
    sub_desc = type_desc[5:-1]
    sub_blocks = _split_brackets(sub_desc, delimiter=",")
    if len(sub_blocks) != 2:
        raise ValueError(f"Invalid Dict type: '{type_desc}'")
    key_type = _parse_type(sub_blocks[0])
    value_type = _parse_type(sub_blocks[1])
    return (("dict",) + (key_type,) + ((value_type),),)


def _parse_tuple(type_desc: str) -> Tuple:
    """Parse a "tuple" type description."""
    sub_desc = type_desc[6:-1]
    sub_blocks = _split_brackets(sub_desc, delimiter=",")
    types: Tuple = ()
    for sub_block in sub_blocks:
        types += (_parse_type(sub_block),)
    return (("tuple",) + types,)


def _parse_optional(type_desc: str) -> Tuple:
    """Parse an "optional" type description."""
    sub_desc = type_desc[9:-1]
    if len(_split_brackets(sub_desc, delimiter=",")) > 1:
        raise ValueError(f"Invalid Optional type: '{type_desc}'")
    return ((type(None),) + _parse_type(sub_desc),)


def _parse_union(type_desc: str) -> Tuple:
    """Parse an "union" type description."""
    sub_desc = type_desc[6:-1]
    # Split by comma
    sub_blocks = _split_brackets(sub_desc, delimiter=",")
    if len(sub_blocks) < 2:
        raise ValueError(f"Invalid Union type: '{type_desc}'")
    types: Tuple = ()
    union_types = [_parse_type(sub_block) for sub_block in sub_blocks]
    for union_type in union_types:
        types += union_type
    return types


def _split_brackets(type_desc: str, delimiter: str) -> List[str]:
    """Split a type description in blocks enclosed by brackets."""
    blocks = []
    bracket_count = 0
    i, j = 0, 0
    while j < len(type_desc):
        char = type_desc[j]
        if char == "[":
            bracket_count += 1
        elif char == "]":
            bracket_count -= 1
        if bracket_count == 0 and char == delimiter:
            blocks.append(type_desc[i:j])
            i = j + 1
            j += 2
        else:
            j += 1
    blocks.append(type_desc[i:j])
    return blocks


def _isinstance(obj: object, types: Union[Type, Tuple]) -> bool:
    """Check if an object is an instance of a type or a tuple of types.

    Intended to work with the outputs of _parse_type.
    """
    if isinstance(types, type):
        return isinstance(obj, types)
    if types[0] == "list" and len(types) == 2:
        return isinstance(obj, list) and all(
            _isinstance(elem, types[1]) for elem in obj
        )
    if types[0] == "set" and len(types) == 2:
        return isinstance(obj, set) and all(
            _isinstance(elem, types[1]) for elem in obj
        )
    if types[0] == "dict" and len(types) == 3:
        return (
            isinstance(obj, dict)
            and all(_isinstance(key, types[1]) for key in obj)
            and all(_isinstance(value, types[2]) for value in obj.values())
        )
    if types[0] == "tuple" and len(types) >= 2:
        return isinstance(obj, tuple) and all(
            _isinstance(elem, types[i + 1]) for i, elem in enumerate(obj)
        )
    if isinstance(types[0], (type, tuple)):
        return any(_isinstance(obj, sub_types) for sub_types in types)
    raise ValueError(f"Invalid type for _isinstance: '{types}'")


def _convert_type(obj: Any, types: Union[Type, Tuple]) -> Any:
    """Try to convert an object to a type or a tuple of types.

    Intended to work with the outputs of _parse_type.
    """
    try:
        return _convert_type_internal(obj, types)
    except (TypeError, ValueError):
        return obj


def _convert_type_internal(obj: Any, types: Union[Type, Tuple]) -> Any:
    """Try to convert an object to a type or a tuple of types.

    Intended to work with the outputs of _parse_type.
    """
    if isinstance(types, type):
        return types(obj)
    if types[0] in ("list", "set") and len(types) == 2:
        type_to_use = locate(types[0])  # list or set
        return type_to_use(
            _convert_type_internal(elem, types[1]) for elem in obj
        )  # type: ignore
    if types[0] == "dict" and len(types) == 3:
        return {
            _convert_type_internal(key, types[1]): _convert_type_internal(
                value, types[2]
            )
            for key, value in obj.items()
        }
    if types[0] == "tuple" and len(types) >= 2:
        return tuple(
            _convert_type_internal(elem, types[i + 1]) for i, elem in enumerate(obj)
        )
    if isinstance(types[0], (type, tuple)):
        if any(_isinstance(obj, sub_types) for sub_types in types):
            return obj
        for sub_types in types:
            try:
                return _convert_type_internal(obj, sub_types)
            except (TypeError, ValueError):
                pass
    raise TypeError
