"""Private module with type parser for processing module with type manipulation."""
from pydoc import locate
from typing import List, Optional, Set, Type


def _parse_type(type_desc: str) -> Set[Type]:
    """Parse a type description.

    Allow basic types (none, any, bool, int, float, str, list, dict), nested lists,
    nested dicts, unions (with Union or the '|' symbol) and Optional.

    Raises
    ------
    ValueError
        If the type description is not valid or not recognized.
    """
    # Clean up
    old_type_desc = type_desc
    type_desc = type_desc.replace(' ', '').lower()
    try:
        # Base type
        base_type = _parse_base_type(type_desc)
        if base_type is not None:
            return {base_type}
        # Split the external blocks enclosed by brackets
        blocks = _split_brackets(type_desc, delimiter='|')
        types: Set[Type] = set()
        for block in blocks:
            if block[:5] == 'list[':
                types.add(list)
            elif block[:9] == 'optional[':
                sub_desc = block[9:-1]
                types.add(type(None))
                types = types.union(_parse_type(sub_desc))
            elif block[:5] == 'dict[':
                types.add(dict)
            elif block[:6] == 'union[':
                sub_desc = block[6:-1]
                # Split by comma
                sub_blocks = _split_brackets(sub_desc, delimiter=',')
                union_types = [_parse_type(sub_block) for sub_block in sub_blocks]
                for union_type in union_types:
                    types = types.union(union_type)
            else:  # Should be a base type
                base_type = _parse_base_type(block)
                if base_type is not None:
                    types.add(base_type)
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
    if type_desc == 'none':
        return type(None)
    if type_desc == 'any':
        # Match any type
        return object
    if type_desc in ('bool', 'int', 'float', 'str', 'list', 'dict'):
        return locate(type_desc)  # type: ignore
    return None


def _split_brackets(type_desc: str, delimiter: str) -> List[str]:
    """Split a type description in blocks enclosed by brackets."""
    blocks = []
    bracket_count = 0
    i, j = 0, 0
    while j < len(type_desc):
        char = type_desc[j]
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
        if bracket_count == 0 and char == delimiter:
            blocks.append(type_desc[i:j])
            i = j + 1
            j += 2
        else:
            j += 1
    blocks.append(type_desc[i:j])
    return blocks
