"""Saving and loading functions of configuration files."""
import os
from typing import Any, Dict, List, Optional

import yaml

from cliconfig.routines import merge_config_file


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
    default_config_paths: Optional[List[str]] = None,
    *,
    allow_new_keys: bool = True,
) -> Dict[str, Any]:
    """Load config from a file and merge into optional default configs.

    Parameters
    ----------
    path : str
        The path to the file to load the configuration.
    default_config_paths : Optional[List[str]], optional
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
    if default_config_paths:
        for config_path in default_config_paths:
            config = merge_config_file(config, config_path, allow_new_keys=True)
    config = merge_config_file(config, path, allow_new_keys=allow_new_keys)
    return config
