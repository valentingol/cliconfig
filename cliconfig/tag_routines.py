"""Routines to manipulate the tags on the keys of a dict.

Used by the processing functions.
"""
import copy
import re
from typing import Any, Dict, List, Tuple


def clean_tag(flat_key: str, tag_name: str) -> str:
    """Clean a tag from a flat key.

    It removes all occurrences of the tag with the exact name.

    Parameters
    ----------
    flat_key : str
        The flat key to clean.
    tag_name : str
        The name of the tag to remove, with or without the '@' prefix.

    Returns
    -------
    flat_key : str
        The cleaned flat key.

    Note
    ----
        ``tag_name`` is supposed to be the exact name of the tag.

    Examples
    --------
    ::

        >>> clean_tag('abc@tag.def@tag_2.ghi@tag', 'tag')
        abc.def@tag_2.ghi
    """
    if tag_name[0] == "@":
        tag_name = tag_name[1:]
    # Replace "@tag@other_tag" by "@other_tag"
    parts = flat_key.split(f"@{tag_name}@")
    flat_key = "@".join(parts)
    # Replace "@tag." by "."
    parts = flat_key.split(f"@{tag_name}.")
    flat_key = ".".join(parts)
    # Remove "@tag" at the end of the string
    if flat_key.endswith(f"@{tag_name}"):
        flat_key = flat_key[: -len(f"@{tag_name}")]
    return flat_key


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
    list_keys = flat_key.split(".")
    for i, key in enumerate(list_keys):
        key = re.sub(r"@.*", "", key)
        list_keys[i] = key
    flat_key = ".".join(list_keys)
    return flat_key


def dict_clean_tags(flat_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Clean a dict from all tags and return the list of keys with tags.

    Parameters
    ----------
    flat_dict : Dict[str, Any]
        The flat dict to clean.

    Returns
    -------
    clean_dict : Dict[str, Any]
        The cleaned flat dict without tags in the keys.
    tagged_keys : List[str]
        The list of keys with tags that have been cleaned.
    """
    items = list(flat_dict.items())
    clean_dict = copy.deepcopy(flat_dict)
    tagged_keys = []
    for key, value in items:
        if "@" in key:
            del clean_dict[key]
            clean_dict[clean_all_tags(key)] = value
            tagged_keys.append(key)
    return clean_dict, tagged_keys


def is_tag_in(flat_key: str, tag_name: str, *, full_key: bool = False) -> bool:
    """Check if a tag is in a flat key.

    The tag name must be the exact name, with or without the "@".
    It supports the case where there are other tags that are prefixes
    or suffixes of the considered tag.

    Parameters
    ----------
    flat_key : str
        The flat key to check.
    tag_name : str
        The name of the tag to check, with or without the '@' prefix.
    full_key : bool, optional
        If True, check for the full key. If False, check for the last part of
        the flat key (after the last dot) that correspond to the parameter name.
        By default, False.

    Returns
    -------
    bool
        True if the tag is in the flat key, False otherwise.
    """
    if tag_name[0] == "@":
        tag_name = tag_name[1:]
    if not full_key:
        flat_key = flat_key.split(".")[-1]
    is_in = (
        flat_key.endswith(f"@{tag_name}")
        or f"@{tag_name}@" in flat_key
        or f"@{tag_name}." in flat_key
    )
    return is_in
