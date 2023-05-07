"""Routines to manipulate configuration as mixed nested and flat dictionaries."""

from typing import Any, Dict, Union

import yaml
from flatten_dict import flatten, unflatten


def merge_config(
    config1: Dict[str, Any],
    config2: Dict[str, Any],
    *,
    allow_new_keys: bool = True,
) -> Dict[str, Any]:
    """Flatten, merge config2 into config1, then unflatten merged config.

    Work even if config1 and config2 have some flat keys (like `{'a.b': ...}`).

    Parameters
    ----------
    config1 : Dict[str, Any]
        The first configuration.
    config2 : Dict[str, Any]
        The second configuration to merge into config1.
    allow_new_keys : bool, optional
        If True, new keys (that are not in config1) are allowed in config2.
        By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and config2 has new keys that are not in config1.
    ValueError
        If there are conflicting keys when flatten one of the config.
        See examples. You may consider calling :func:`clean_pre_flat` on the input
        configs in that case.

    Returns
    -------
    config : Dict[str, Any]
        The merged nested/unflatten config (no flat keys).

    Examples
    --------
    ::

        >>> merge_config({'a.b': 1, 'a': {'c': 2}},  {'c': 3}, allow_new_keys=True)
        {'a': {'b': 1, 'c': 2}, 'c': 3}
        >>> merge_config({'a.b': 1, 'a': {'c': 2}},  {'c': 3}, allow_new_keys=False)
        ValueError: New parameter found 'c' that is not in the original config.
        >>> merge_config({'a.b': 1, 'a': {'b': 1}},  {'c': 3}, allow_new_keys=True)
        ValueError: duplicated key 'a.b'.
        The above exception was the direct cause of the following exception:
        ValueError: You may consider calling `clean_pre_flat` on config1 before merging.
    """
    # Flatten configs
    flatten_configs = []
    for i, config in enumerate([config1, config2]):
        try:
            flatten_config = flat_config(config)
        except ValueError as exc:
            raise ValueError(
                f"Duplicated key found in config {i + 1} when flattening. "
                f"You may consider calling `clean_pre_flat` before merging."
            ) from exc
        flatten_configs.append(flatten_config)
    config1_flat, config2_flat = flatten_configs[0], flatten_configs[1]

    if not allow_new_keys:
        # Check that there are no new keys in config2
        for key in config2_flat:
            if key not in config1_flat.keys():
                raise ValueError(
                    f"New parameter found '{key}' in that is not in the original "
                    "config."
                )
    # Merge flat configs
    flatten_config = {**config1_flat, **config2_flat}
    # Unflatten config
    config = unflat_config(flatten_config)
    return config


def merge_config_file(
    config_or_path1: Union[str, Dict[str, Any]],
    config_or_path2: Union[str, Dict[str, Any]],
    *,
    allow_new_keys: bool = True,
) -> Dict[str, Any]:
    """Merge two configs or their paths into one (config2 into config1).

    Similar to :func:`cliconfig.routines.merge_config` but allow passing
    the paths of config as inputs.

    Parameters
    ----------
    config_or_path1 : Union[str, Dict[str, Any]]
        The first configuration or its path.
    config_or_path2 : Union[str, Dict[str, Any]]
        The second configuration or its path to merge into first configuration.
    allow_new_keys : bool, optional
        If True, new keys (that are not in config1) are allowed in config2.
        By default True.

    Returns
    -------
    config : Dict[str, Any]
        The merged nested config (no flat keys).
    """
    configs = []
    for config_or_path in [config_or_path1, config_or_path2]:
        if isinstance(config_or_path, str):
            path = config_or_path
            with open(path, "r", encoding="utf-8") as cfg_file:
                config = yaml.safe_load(cfg_file)
        else:
            config = config_or_path
        configs.append(config)
    config1, config2 = configs[0], configs[1]
    config = merge_config(
        config1,
        config2,
        allow_new_keys=allow_new_keys,
    )
    return config


def flat_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten config then return it.

    Work even if config has some flat keys as long as there are no
    conflicts (see examples section).

    Parameters
    ----------
    config : Dict[str, Any]
        The configuration to flatten.

    Raises
    ------
    ValueError
        If config has some conflicting keys (like `{'a.b': ..., 'a': {'b': ...}}`).

    Returns
    -------
    config : Dict[str, Any]
        The flattened config.

    Notes
    -----
        Nested empty dict are ignored even if they are conflicting (see last example).

    Examples
    --------
    ::

        >>> flat_config({'a.b': 1, 'a': {'c': 2}, 'd': 3})
        {'a.b': 1, 'a.c': 2, 'd': 3}
        >>> flat_config({'a.b': 1, 'a': {'b': 1}})
        ValueError: duplicated key 'a.b'
        >>> flat_config({'a.b': 1, 'a': {'c': {}}, 'a.c': 3})
        {'a.b': 1, 'a.c': 3}

    """
    return flatten(config, reducer="dot")


def unflat_config(flatten_config: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten a flat config then return it.

    Parameters
    ----------
    flatten_config : Dict[str, Any]
        The configuration to flatten. Must be flat.

    Raises
    ------
    ValueError
        If flatten_config is not flat and then found conflicts.

    Returns
    -------
    config : Dict[str, Any]
        The flattened config.

    Examples
    --------
    ::

        >>> unflat_config({'a.b': 1, 'a.c': 2, 'c': 3})
        {'a': {'b': 1, 'c': 2}, 'c': 3}
        >>> unflat_config({'a.b': 1, 'a': {'c': 2}})
        ValueError: duplicated key 'a'
        The config must be flatten before calling unflat_config function.
    """
    try:
        config = unflatten(flatten_config, splitter="dot")
    except ValueError as exc:
        raise ValueError(
            "The config must be flatten before calling unflat_config function."
        ) from exc
    return config


def clean_pre_flat(config: Dict[str, Any], priority: str) -> Dict[str, Any]:
    """Remove keys in config that may cause conflicts when flattening.

    Parameters
    ----------
    config: Dict[str, Any]
        The configuration to clean.
    priority: str
        One of 'flat' or 'unflat', 'error'.
        If 'flat', keys with dots at the root like `{'a.b': ...}` (flat keys) have
        priority over unflat keys like `{'a': {'b': ...}}` when there are conflicts.
        If 'unflat', unflat keys have priority over flat keys when there are conflicts.
        If 'error', raise an error when there are conflicts.

    Raises
    ------
    ValueError
        If priority is not one of 'flat', 'unflat' or 'nothing'.

    Returns
    -------
    config: Dict[str, Any]
        The cleansed configuration.

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
        flat_part = dict(filter(lambda items: "." in items[0], config.items()))
        unflat_part = dict(filter(lambda items: "." not in items[0], config.items()))
        unflat_part_flat = flat_config(unflat_part)
        if priority == "unflat":
            for key in flat_part:
                if key in unflat_part_flat:
                    _del_key(config, key, keep_flat=False, keep_unflat=True)
        else:
            for key in unflat_part_flat:
                if key in flat_part:
                    _del_key(config, key, keep_flat=True, keep_unflat=False)
    elif priority == "error":
        flat_config(config)  # Will raise an error if there are conflicts
    else:
        raise ValueError(
            "priority argument must be one of 'flat', 'unflat' or 'error' but "
            f"found '{priority}'."
        )
    return config


def _del_key(
    config: Dict[str, Any],
    flat_key: str,
    *,
    keep_flat: bool = False,
    keep_unflat: bool = False,
) -> Dict[str, Any]:
    """Remove a value in config dict corresponding to a flat key (e.g. 'a.b.c).

    Parameters
    ----------
    config: Dict[str, Any]
        The configuration to clean. There could be a mix of flat and unflat keys.
    flat_key: str
        The flat key to remove. E.g. 'a.b.c'.
    keep_flat: bool, optional
        If True, keep the flat key in the config dict. By default False.
    keep_unflat: bool, optional
        If True, keep the unflat key in the config dict. By default False.

    Raises
    ------
    ValueError
        If the key is not found in the config dict.

    Returns
    -------
    config: Dict[str, Any]
        The new configuration.

    Examples
    --------
    ::

        >>> _del_key({'a': {'b': {'c': 1}, 'd': 2}, 'a.e': 3, 'a.b.c': 4}, 'a.b.c')
        {'a': {'d': 2}, 'a.e': 3}
        >>> _del_key({'a': {'b': {'c': 1}, 'd': 2}, 'a.e': 3, 'a.b.c': 4}, 'a.b.c',
                    keep_flat=True)
        {'a': {'d': 2}, 'a.e': 3, 'a.b.c': 4}
        >>> _del_key({'a': {'b': {'c': 1}, 'd': 2}, 'a.e': 3, 'a.b.c': 4}, 'a.b.c',
                    keep_unflat=True)
        {'a': {'b': {'c': 1}, 'd': 2}, 'a.e': 3}
        >>> _del_key({'a': {'b': {'c': 1}, 'd': 2}, 'a.e': 3, 'a.b.c': 4}, 'a.b.z')
        ValueError: Key 'a.b.z' not found in config.
        >>> _del_key({'a': {'b': {'c': 1}, 'd': 2}, 'a.e': 3, 'a.b.c': 4}, 'a.z.c')
        ValueError: Key 'a.z.c' not found in config.

    """
    found_key = False
    if not keep_flat and flat_key in config:
        # Remove flat_key if it exists at the root
        found_key = True
        del config[flat_key]

    def recursive_del_key(config: Dict[str, Any], key: str, *, found_key: bool) -> bool:
        first_key, *other_keys = key.split(".", 1)
        if other_keys:
            if first_key in config:
                # Delete key in sub-dict
                new_key = recursive_del_key(
                    config[first_key],
                    ".".join(other_keys),
                    found_key=found_key,
                )
                found_key = found_key or new_key
                # Remove if empty
                if config[first_key] == {}:
                    del config[first_key]
            else:
                # No key found, return input found_key
                return found_key
        else:
            if first_key in config:
                found_key = True
                del config[first_key]
            else:
                # No key found, return input found_key
                return found_key
        return found_key

    if not keep_unflat:
        # Remove flat_key if it exists in a nested dict
        found_key = recursive_del_key(config, flat_key, found_key=found_key)
    # Raise error if key not found
    if not found_key:
        raise ValueError(f"Key '{flat_key}' not found in config.")
    return config
