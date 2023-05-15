"""Parser for CLI commands."""
from typing import Any, Dict, List, Tuple

import yaml


def parse_cli(sys_argv: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """Parser for CLI commands.

    Return list of config path(s) that are detected with ``--config`` followed
    by a space. If multiple paths are provided, they must be separated by a comma
    and no space around the comma. It also possible to provide a list of paths.

    Return also a dictionary of parameters from CLI detected with ``--<key>=<value>``
    (with "=" and without spaces around). If no value is provided,
    it is True by default (like for a flag).

    Parameters
    ----------
    sys_argv : List[str]
        List of arguments from sys.argv.

    Raises
    ------
    Value Error
        If the ``--config`` argument (with space) is used more than once.

    Returns
    -------
    config_paths : List[str]
        List of paths to config files to merge.
    cli_params_dict : Dict[str, Any]
        Dictionary of parameters from CLI.

    Examples
    --------
    .. code-block:: text

        $ python my_script.py --config config.yaml --foo.bar.param=[1, 2, 3]

    Will be parsed as ``config_paths=['config.yaml']``
    and ``cli_params={'foo.bar.param': [1, 2, 3]}``.
    It is equivalent to: ``{'foo': {'bar': {'param': [1, 2, 3]}}`` for
    :func:`.merge_flat` and :func:`.make_config`.
    """
    cli_params_dict: Dict[str, Any] = {}
    config_paths: List[str] = []
    i = 0
    while i < len(sys_argv):
        elem = sys_argv[i]
        if elem == "--config":
            if config_paths:
                raise ValueError(
                    "Only one '--config ' argument is allowed in CLI (used for "
                    "config merging)."
                )
            configs = yaml.safe_load(sys_argv[i + 1])
            if isinstance(configs, list):
                config_paths = configs
            if isinstance(configs, str):
                config_paths = sys_argv[i + 1].split(",")
            i += 2
        elif elem.startswith("--"):
            splits = elem.split("=", maxsplit=1)
            if len(splits) == 2:
                key, value_str = splits
            else:
                key = splits[0]
                # If no value is provided, use True because it could
                # be seen as a flag
                value_str = "true"
            key = key[2:]
            value = yaml.safe_load(value_str)
            cli_params_dict[key] = value
            i += 1
        else:  # Not a config parameter
            i += 1
    return config_paths, cli_params_dict
