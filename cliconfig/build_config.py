"""Functions to build config dict."""

import sys
from typing import Any, Dict

from cliconfig.cli_parser import parse_cli
from cliconfig.routines import merge_config, merge_config_file


def make_config(
    *default_config_paths: str, allow_new_keys: bool = False
) -> Dict[str, Any]:
    r"""Make a config from default configs and CLI arguments.

    It uses the CLI Config routines to parse the CLI arguments and merge
    them in a simple way.

    Parameters
    ----------
    default_config_paths : Tuple[str]
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

    Examples
    --------
    ::

        # main.py
        config = make_config('data.yaml', 'model.yaml', 'train.yaml')

    .. code-block:: text

        python main.py -- config bestmodel.yaml,mydata.yaml \
            --architecture.layers.hidden_dim 64

    """
    config: Dict[str, Any] = {}
    config_paths, config_cli_params = parse_cli(sys.argv)
    print(
        f"[CONFIG] Merge {len(default_config_paths)} default configs, "
        f"{len(config_paths)} additional configs and "
        f"{len(config_cli_params)} CLI parameter(s)."
    )
    for default_config_path in default_config_paths:
        config = merge_config_file(config, default_config_path)

    for config_path in config_paths:
        config = merge_config_file(config, config_path, allow_new_keys=allow_new_keys)
    config = merge_config(config, config_cli_params, allow_new_keys=allow_new_keys)
    return config
