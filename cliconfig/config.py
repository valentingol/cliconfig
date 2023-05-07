"""Functions to manipulate configuration as nested dictionaries."""
import os
import sys
from typing import Any, Dict, List, Optional

import yaml
from flatten_dict import flatten, unflatten

from cliconfig.cli_parser import parse


def make_config(*default_configs: str, allow_new_keys: bool = False) -> Dict[str, Any]:
    """Make a config from default configs and CLI arguments.

    Parameters
    ----------
    default_configs : Tuple[str]
        Paths to default configs. They are merged in order and new keys
        are allowed.
    allow_new_keys : bool, optional
        If True, new keys in CLI are allowed in merged config. Otherwise,
        it raises an error. By default False.

    Raises
    ------
    ValueError
        If allow_new_keys is False and CLI has new keys that are not
        in default configs.

    Returns
    -------
    config : Dict[str, Any]
        The merged config.
    """
    config: Dict[str, Any] = {}
    config_paths, config_cli_params = parse(sys.argv)
    print(
        f"[CONFIG] Merge {len(default_configs)} default configs, "
        f"{len(config_paths)} additional configs and "
        f"{len(config_cli_params)} CLI parameter(s)."
    )
    for default_config_path in default_configs:
        with open(default_config_path, "r", encoding="utf-8") as cfg_file:
            default_config = yaml.safe_load(cfg_file)
        config = merge_config(config, default_config, allow_new_keys=True)

    for config_path in config_paths:
        with open(config_path, "r", encoding="utf-8") as cfg_file:
            additional_config = yaml.safe_load(cfg_file)
        config = merge_config(config, additional_config, allow_new_keys=allow_new_keys)
    config = merge_config(config, config_cli_params, allow_new_keys=allow_new_keys)
    return config


def merge_config(
    config1: Dict[str, Any],
    config2: Dict[str, Any],
    *,
    allow_new_keys: bool = True,
    priority: str = "flat",
) -> Dict[str, Any]:
    """Merge config2 into config1.

    Parameters
    ----------
    config1 : Dict[str, Any]
        The first configuration.
    config2 : Dict[str, Any]
        The second configuration to merge into config1.
    allow_new_keys : bool, optional
        If True, new keys (that are not in config1) are allowed in config2.
        By default True.
    priority : str, optional
        One of 'flat' or 'unflat'.
        If 'flat', keys with dots at the root like `{'a.b': ...}` (flat keys) have
        priority over unflat keys like `{'a': {'b': ...}}` when there are conflicts.
        If 'unflat', unflat keys have priority over flat keys when there are conflicts.

    Raises
    ------
    ValueError
        If priority is not one of 'flat', 'unflat' or 'order'.
    ValueError
        If allow_new_keys is False and config2 has new keys that are not in config1.

    Examples
    --------
    ::

        >>> merge_config({'a.b': 1, 'a': {'b': 2}}, {'c': 3}, allow_new_keys=True,
                         priority='flat')
        {'a.b': 1, 'c': 3}
        >>> merge_config({'a.b': 1, 'a': {'b': 2}}, {'c': 3}, allow_new_keys=True,
                         priority='unflat')
        {'a.b': 2, 'c': 3}
        >>> merge_config({'a.b': 1, 'a': {'b': 2}}, {'c': 3}, allow_new_keys=False,
                         priority='unflat')
        ValueError: New parameter found 'c' that is not in the original config.
    """
    if priority in ("flat", "unflat"):
        # Split flat and unflat keys
        config1_flat = dict(filter(lambda x: "." in x[0], config1.items()))
        config1_unflat = dict(filter(lambda x: "." not in x[0], config1.items()))
        config2_flat = dict(filter(lambda x: "." in x[0], config2.items()))
        config2_unflat = dict(filter(lambda x: "." not in x[0], config2.items()))
        # Flatten unflat keys
        config1_unflat_flat = flatten(config1_unflat, reducer="dot")
        config2_unflat_flat = flatten(config2_unflat, reducer="dot")
        if priority == "flat":
            # Flat keys erase the previous unflat keys with the same name
            config1_flat = {**config1_unflat_flat, **config1_flat}
            config2_flat = {**config2_unflat_flat, **config2_flat}
        else:
            # The previous unflat keys erase the flat keys with the same name
            config1_flat = {**config1_flat, **config1_unflat_flat}
            config2_flat = {**config2_flat, **config2_unflat_flat}
    else:
        raise ValueError(
            f"Unknown dot_prior '{priority}'. Should be one of "
            "'flat', 'unflat' or 'order'."
        )
    if not allow_new_keys:
        # Check that there are no new keys in config2
        for key in config2_flat:
            if key not in config1_flat.keys():
                raise ValueError(
                    f"New parameter found '{key}' that is not in the original config."
                )
    # Merge flat configs
    flat_config = {**config1_flat, **config2_flat}
    # Unflats config
    config = unflatten(flat_config, splitter="dot")
    return config


def save_config(config: Dict[str, Any], path: str) -> None:
    """Save config to a file.

    Parameters
    ----------
    config : Dict[str, Any]
        The configuration to save.
    path : str
        The path to the file to save the configuration.
    """
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    with open(path, "w", encoding="utf-8") as cfg_file:
        yaml.dump(config, cfg_file, default_flow_style=False)


def load_config(
    path: str,
    default_configs: Optional[List[str]] = None,
    *,
    allow_new_keys: bool = True,
) -> Dict[str, Any]:
    """Load config from a file and merge into optional default configs.

    Parameters
    ----------
    path : str
        The path to the file to load the configuration.
    default_configs : Optional[List[str]], optional
        Paths to default configs. They are merged in order, new keys are allowed.
        Then, the loaded config is merged into the result. None for no default configs.
        By default None.
    allow_new_keys : bool, optional
        If True, the new keys in the loaded config are allowed in the merged config.
        Otherwise, it raises an error. By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and the loaded config has new keys that are not
        in default configs.

    Returns
    -------
    config : Dict[str, Any]
        The config merged from default configs and the loaded config.
    """
    config: Dict[str, Any] = {}
    if default_configs:
        for config_path in default_configs:
            with open(config_path, "r", encoding="utf-8") as cfg_file:
                default_config = yaml.safe_load(cfg_file)
            config = merge_config(config, default_config, allow_new_keys=True)
    with open(path, "r", encoding="utf-8") as cfg_file:
        loaded_config = yaml.safe_load(cfg_file)
    config = merge_config(config, loaded_config, allow_new_keys=allow_new_keys)
    return config
