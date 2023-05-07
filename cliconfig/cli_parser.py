"""Parser for CLI commands."""
from typing import Any, Dict, List, Tuple

import yaml


def parse(sys_argv: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """Parser for CLI commands.

    Parameters
    ----------
    sys_argv : List[str]
        List of arguments from sys.argv.

    Returns
    -------
    config_paths : List[str]
        List of paths to config files to merge.
    config_cli_params : Dict[str, Any]
        Dictionary of parameters from CLI.
    """
    config_cli_params: Dict[str, Any] = {}
    config_paths: List[str] = []
    i = 0
    while i < len(sys_argv):
        elem = sys_argv[i]
        if elem == '--config':
            if config_paths:
                raise ValueError(
                    "Only one '--config ' argument is allowed in CLI (used for "
                    "config merging). If you have a subconfig called 'config', "
                    "use '--config=<val>' (with an '=')."
                )
            config_paths = sys_argv[i + 1].split(',')
            i += 2

        elif elem.startswith('--'):
            if '=' in elem:
                key, value_str = elem.split('=', maxsplit=1)
                i += 1
            else:
                key, value_str = elem, sys_argv[i + 1]
                i += 2
            key = key[2:]
            value = yaml.safe_load(value_str)
            config_cli_params[key] = value
        else:
            i += 1
    return config_paths, config_cli_params


if __name__ == '__main__':
    import sys
    print(sys.argv)
