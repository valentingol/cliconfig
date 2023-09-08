"""Routines to manipulate nested and flat dictionaries (and mix of both).

Used by :mod:`.process_routines` and :mod:`.config_routines`.
"""
import os
from typing import Any, Dict, Tuple, Union

import yaml
from flatten_dict import flatten as _flatten
from flatten_dict import unflatten as _unflatten

from cliconfig.yaml_tags._yaml_tags import get_yaml_loader, insert_tags


def merge_flat(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    *,
    allow_new_keys: bool = True,
) -> Dict[str, Any]:
    """Flatten then merge dict2 into dict1. The result is flat.

    Work even if dict1 and dict2 have a mix of nested and flat
    dictionaries. For instance like this:

    .. code-block:: python

        dict1 = {'a.b': 1, 'a': {'c': 2}, 'a.d': {'e.f': 3}}

    Parameters
    ----------
    dict1 : Dict[str, Any]
        The first dict. It can be nested, flat or a mix of both.
    dict2 : Dict[str, Any]
        The second dict to merge into first dict.
    allow_new_keys : bool, optional
        If True, new keys (that are not in dict1) are allowed in dict2.
        By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and dict2 has new keys that are not in dict1.
    ValueError
        If there are conflicting keys when flatten one of the dicts.
        See last example. You may consider calling :func:`clean_pre_flat` on the input
        dicts in that case.

    Returns
    -------
    flat_dict : Dict[str, Any]
        The flat dict (all keys are at the root and separated by dots).

    Examples
    --------
    ::

        >>> merge_dict({'a.b': 1, 'a': {'c': 2}},  {'c': 3}, allow_new_keys=True)
        {'a.b': 1, 'a.c': 2, 'c': 3}
        >>> merge_dict({'a.b': 1, 'a': {'c': 2}},  {'c': 3}, allow_new_keys=False)
        ValueError: New parameter found 'c' that is not in the original dict.
        >>> merge_dict({'a.b': 1, 'a': {'b': 1}},  {'c': 3}, allow_new_keys=True)
        ValueError: duplicated key 'a.b'.
        The above exception was the direct cause of the following exception:
        ValueError: You may consider calling 'clean_pre_flat' on dict 1 before merging.
    """
    # Flatten dicts
    flat_dict1, flat_dict2 = _flat_before_merge(dict1, dict2)

    if not allow_new_keys:
        # Check that there are no new keys in dict2
        for key in flat_dict2:
            if key not in flat_dict1:
                raise ValueError(
                    f"New parameter found '{key}' in that is not in the original "
                    "dict."
                )
    # Merge flat dicts
    flat_dict = {**flat_dict1, **flat_dict2}
    return flat_dict


def _flat_before_merge(
    dict1: Dict[str, Any], dict2: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Flatten two dicts to merge them later."""
    # Flatten dicts
    flat_dicts = []
    for i, _dict in enumerate([dict1, dict2]):
        # Check if already flat
        is_flat = all(not isinstance(val, dict) for val in _dict.values())
        if not is_flat:
            try:
                flat_dict = flatten(_dict)
            except ValueError as exc:
                raise ValueError(
                    f"Duplicated key found in dict {i + 1} when flattening. "
                    f"You may consider calling 'clean_pre_flat' before merging."
                ) from exc
        else:
            flat_dict = _dict
        flat_dicts.append(flat_dict)
    return flat_dicts[0], flat_dicts[1]


def merge_flat_paths(
    dict_or_path1: Union[str, Dict[str, Any]],
    dict_or_path2: Union[str, Dict[str, Any]],
    *,
    allow_new_keys: bool = True,
) -> Dict[str, Any]:
    """Flatten then merge two dict eventually loaded from yaml file paths.

    Similar to :func:`.merge_flat` but allow passing the paths of dicts
    as inputs. It merges the second dict into the first one.

    Parameters
    ----------
    dict_or_path1 : Union[str, Dict[str, Any]]
        The first dict or its path.
    dict_or_path2 : Union[str, Dict[str, Any]]
        The second dict or its path, to merge into first dict.
    allow_new_keys : bool, optional
        If True, new keys (that are not in dict1) are allowed in dict2.
        By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and dict2 has new keys that are not in dict1.
    ValueError
        If there are conflicting keys when flatten one of the dicts.
        See last example. You may consider calling :func:`clean_pre_flat` on the input
        dicts in that case.

    Returns
    -------
    flat_dict : Dict[str, Any]
        The flat dict (all keys are at the root and separated by dots).
    """
    dicts = []
    for dict_or_path in [dict_or_path1, dict_or_path2]:
        if isinstance(dict_or_path, str):
            _dict = load_dict(dict_or_path)
        else:
            _dict = dict_or_path
        dicts.append(_dict)
    dict1, dict2 = dicts[0], dicts[1]
    flat_dict = merge_flat(
        dict1,
        dict2,
        allow_new_keys=allow_new_keys,
    )
    return flat_dict


def flatten(in_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten dict then return it (flat keys are built with dots).

    Work even if in_dict is a mix of nested and flat dictionaries.
    For instance like this:

    .. code-block:: python

        >>> flatten({'a.b': {'c': 1}, 'a': {'b.d': 2}, 'a.e': {'f.g': 3}})
        {'a.b.c': 1, 'a.b.d': 2, 'a.e.f.g': 3}


    Parameters
    ----------
    in_dict : Dict[str, Any]
        The dict to flatten. It can be nested, already flat or a mix of both.

    Raises
    ------
    ValueError
        If dict has some conflicting keys (like ``{'a.b': <x>, 'a': {'b': <y>}}``).

    Returns
    -------
    flat_dict : Dict[str, Any]
        The flattened dict.

    Note
    ----
        Nested empty dict are ignored even if they are conflicting (see last example).

    Examples
    --------
    ::

        >>> flatten({'a.b': 1, 'a': {'c': 2}, 'd': 3})
        {'a.b': 1, 'a.c': 2, 'd': 3}
        >>> flatten({'a.b': {'c': 1}, 'a': {'b.d': 2}, 'a.e': {'f.g': 3}})
        {'a.b.c': 1, 'a.b.d': 2, 'a.e.f.g': 3}
        >>> flatten({'a.b': 1, 'a': {'b': 1}})
        ValueError: duplicated key 'a.b'
        >>> flatten({'a.b': 1, 'a': {'c': {}}, 'a.c': 3})
        {'a.b': 1, 'a.c': 3}

    """
    flat_dict = _flatten(in_dict, reducer="dot")
    return flat_dict


def unflatten(flat_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Unflatten a flat dict then return it.

    Parameters
    ----------
    flat_dict : Dict[str, Any]
        The dict to unflatten. Must be a fully flat dict (depth of 1 with keys
        separated by dots).

    Raises
    ------
    ValueError
        If flat_dict is not flat and then found conflicts.

    Returns
    -------
    unflat_dict : Dict[str, Any]
        The output nested dict.

    Examples
    --------
    ::

        >>> unflatten({'a.b': 1, 'a.c': 2, 'c': 3})
        {'a': {'b': 1, 'c': 2}, 'c': 3}
        >>> unflatten({'a.b': 1, 'a': {'c': 2}})
        ValueError: duplicated key 'a'
        The dict must be flatten before calling unflatten function.
    """
    try:
        unflat_dict = _unflatten(flat_dict, splitter="dot")
    except ValueError as exc:
        raise ValueError(
            "The dict must be flatten before calling unflatten function."
        ) from exc
    return unflat_dict


def clean_pre_flat(in_dict: Dict[str, Any], priority: str) -> Dict[str, Any]:
    """Remove keys in input dict that may cause conflicts when flattening.

    Parameters
    ----------
    in_dict : Dict[str, Any]
        The dict to clean. It must be the union of a fully flat dict
        (no nested dict i values) and a fully nested dict (without dots in keys).
        See warning section below.
    priority: str
        One of 'flat' or 'unflat', 'error'.
        If 'flat', keys with dots at the root like ``{'a.b': ...}`` (flat keys) have
        priority over nested keys like ``{'a': {'b': ...}}`` when there are conflicts.
        If 'unflat', nested keys have priority over flat keys when there are conflicts.
        If 'error', raise an error when there are conflicts.

    Raises
    ------
    ValueError
        If priority is not one of 'flat', 'unflat' or 'error'.

    Returns
    -------
    Dict[str, Any]
        The cleansed dict.

    Warning
    -------
        * No flat key can contain a dict. Then, dicts like ``{'a.b': {'c': 1}}``
          are not supported.
        * All the keys that contain dots (the flat keys) must be at the root.
          Then, dicts like ``{a: {'b.c': 1}}`` are not supported.
        * To summarize, the dict must contain only fully flat dicts
          and/or fully nested dicts.

    Examples
    --------
    ::

        >>> clean_pre_flat({'a.b': 1, 'a': {'b': 2}, 'c': 3}, priority='flat')
        {'a.b': 1, 'c': 3}
        >>> clean_pre_flat({'a.b': 1, 'a': {'b': 2}, 'c': 3}, priority='unflat')
        {'a': {'b': 2}, 'c': 3}
        >>> clean_pre_flat({'a.b': 1, 'a': {'b': 2}, 'c': 3}, priority='error')
        ValueError: duplicated key 'a.b'
    """
    if priority in ("flat", "unflat"):
        # Check that there are no conflicts
        flat_part = dict(filter(lambda items: "." in items[0], in_dict.items()))
        unflat_part = dict(filter(lambda items: "." not in items[0], in_dict.items()))
        unflat_part_flat = flatten(unflat_part)
        if priority == "unflat":
            for key in flat_part:
                if key in unflat_part_flat:
                    _del_key(in_dict, key, keep_flat=False, keep_unflat=True)
        else:
            for key in unflat_part_flat:
                if key in flat_part:
                    _del_key(in_dict, key, keep_flat=True, keep_unflat=False)
    elif priority == "error":
        flatten(in_dict)  # Will raise an error if there are conflicts
    else:
        raise ValueError(
            "priority argument must be one of 'flat', 'unflat' or 'error' but "
            f"found '{priority}'."
        )
    return in_dict


def _del_key(
    in_dict: Dict[str, Any],
    flat_key: str,
    *,
    keep_flat: bool = False,
    keep_unflat: bool = False,
) -> None:
    """Remove in place a value in dict corresponding to a flat key (e.g. 'a.b.c').

    Parameters
    ----------
    in_dict : Dict[str, Any]
        The dict to clean. It must be the union of a fully flat dict
        (no nested dict i values) and a fully nested dict (without dots in keys).
        See warning section below.
    flat_key: str
        The flat key to remove. E.g. 'a.b.c'.
    keep_flat: bool, optional
        If True, keep the flat key in the dict. By default False.
    keep_unflat: bool, optional
        If True, keep the unflat key in the dict. By default False.

    Raises
    ------
    ValueError
        If the key is not found in the dict.

    Warning
    -------
        * No flat key can contain a dict. Then, dicts like ``{'a.b': {'c': 1}}``
          are not supported.
        * All the keys that contain dots (the flat keys) must be at the root.
          Then, dicts like ``{a: {'b.c': 1}}`` are not supported.
        * To summarize, the dict must contain only fully flat dicts
          and fully nested dicts.

    Examples
    --------
    ::

        >>> in_dict = {'a': {'b': {'c': 1}, 'd': 2}, 'a.b.c': 4}
        >>> _del_key(in_dict, 'a.b.c'); in_dict
        {'a': {'d': 2}}
        >>> _del_key(in_dict, 'a.b.c', keep_flat=True); in_dict
        {'a': {'d': 2}, 'a.b.c': 4}
        >>> _del_key(in_dict, 'a.b.c', keep_unflat=True); in_dict
        {'a': {'b': {'c': 1}, 'd': 2}}
        >>> _del_key(in_dict, 'a.b.z')
        ValueError: Key 'a.b.z' not found in dict.
        >>> _del_key(in_dict, 'a.z.c')
        ValueError: Key 'a.z.c' not found in dict.
    """
    found_key = False
    if not keep_flat and flat_key in in_dict:
        # Remove flat_key if it exists at the root
        found_key = True
        del in_dict[flat_key]

    def recursive_del_key(
        in_dict: Dict[str, Any], key: str, *, found_key: bool
    ) -> bool:
        first_key, *other_keys = key.split(".", 1)
        if other_keys:
            if first_key in in_dict:
                # Delete key in sub-dict
                new_key = recursive_del_key(
                    in_dict[first_key],
                    ".".join(other_keys),
                    found_key=found_key,
                )
                found_key = found_key or new_key
                # Remove if empty
                if in_dict[first_key] == {}:
                    del in_dict[first_key]
            else:
                # No key found, return input found_key
                return found_key
        else:
            if first_key in in_dict:
                found_key = True
                del in_dict[first_key]
            else:
                # No key found, return input found_key
                return found_key
        return found_key

    if not keep_unflat:
        # Remove flat_key if it exists in a nested dict
        found_key = recursive_del_key(in_dict, flat_key, found_key=found_key)
    # Raise error if key not found
    if not found_key:
        raise ValueError(f"Key '{flat_key}' not found in dict.")


def save_dict(in_dict: Dict[str, Any], path: str) -> None:
    """Save a dict to a yaml file (with yaml.dump).

    Parameters
    ----------
    in_dict : Dict[str, Any]
        The dict to save.
    path : str
        The path to the yaml file to save the dict.
    """
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    with open(path, "w", encoding="utf-8") as cfg_file:
        yaml.dump(in_dict, cfg_file, default_flow_style=False)


def load_dict(path: str) -> Dict[str, Any]:
    """Load dict from a yaml file path.

     Support multiple files in the same document and yaml tags.

    Parameters
    ----------
    path : str
        The path to the file to load the dict.

    Returns
    -------
    out_dict : Dict[str, Any]
        The nested (unflatten) loaded dict.

    Note
    ----

        * If multiple yaml files are in the same document, they are merged
        from the first to the last.
        * To use multiple yaml tags, separate them with "@". E.g. ``!tag1@tag2``.
        * You can combine any number of yaml and cliconfig tags together.
    """
    with open(path, "r", encoding="utf-8") as cfg_file:
        file_dicts = yaml.load_all(cfg_file, Loader=get_yaml_loader())
        out_dict: Dict[str, Any] = {}
        for file_dict in file_dicts:
            new_dict, _ = insert_tags(file_dict)
            out_dict = merge_flat(out_dict, new_dict, allow_new_keys=True)
    return unflatten(out_dict)


def show_dict(in_dict: Dict[str, Any], start_indent: int = 0) -> None:
    """Show the input dict in a pretty way.

    The config dict is automatically unflattened before printing.

    Parameters
    ----------
    in_dict : Dict[str, Any]
        The dict to show.
    start_indent : int, optional
        The number of starting tab indent (4 spaces), by default 0.
    """

    def pretty_print(in_dict: Dict[str, Any], indent: int) -> None:
        """Pretty print the dict recursively."""
        for key, value in in_dict.items():
            print(f"{'    ' * indent}{key}: ", end="")
            if isinstance(value, dict):
                print()
                pretty_print(value, indent + 1)
            elif isinstance(value, str):
                print(f"'{value}'")
            else:
                print(value)

    pretty_print(unflatten(in_dict), start_indent)
