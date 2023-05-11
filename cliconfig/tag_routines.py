"""Routines to manipulate the tags on the keys of a dict."""
import copy
import re
from typing import Any, Dict, List, Tuple


def clean_tag(flat_key: str, tag_name: str) -> str:
    """Clean a tag from a flat key.

    It removes all occurences of the tag with the exact name.

    flat_key : str
        The flat key to clean.
    tag_name : str
        The name of the tag to remove, with or without the '@' prefix.

    Note
    ----
        `tag_name` is supposed to be the exact name of the tag.

    Examples
    --------
    ::

        >>> clean_tag('abc@tag.def@tag_2.ghi@tag', 'tag')
        abc.def@tag_2.ghi
    """
    if tag_name[0] == "@":
        tag_name = tag_name[1:]
    # Replace "@tag@other_tag" by "@other_tag"
    parts = flat_key.split(f'@{tag_name}@')
    flat_key = "@".join(parts)
    # Replace "@tag." by "."
    parts = flat_key.split(f'@{tag_name}.')
    flat_key = ".".join(parts)
    # Remove "@tag" at the end of the string
    if flat_key.endswith(f'@{tag_name}'):
        flat_key = flat_key[:-len(f'@{tag_name}')]
    return flat_key


# clean_all_tags, dict_clean_tags

def clean_all_tags(flat_key: str) -> str:
    """Clean all tags from a flat key.

    Parameters
    ----------
    flat_key : str
        The flat key to clean.

    Returns
    -------
    flat_key : str
        The cleaned flat key.
    """
    list_keys = flat_key.split('.')
    for i, key in enumerate(list_keys):
        key = re.sub(r'@.*', '', key)
        list_keys[i] = key
    flat_key = '.'.join(list_keys)
    return flat_key


def dict_clean_tags(flat_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Clean a dict from all tags and return the list of keys with tags."""
    items = list(flat_dict.items())
    clean_dict = copy.deepcopy(flat_dict)
    tagged_keys = []
    for key, value in items:
        if '@' in key:
            del clean_dict[key]
            clean_dict[clean_all_tags(key)] = value
            tagged_keys.append(key)
    return clean_dict, tagged_keys
