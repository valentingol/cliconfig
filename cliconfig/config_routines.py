"""Functions to manipulate config as dict with yaml files and CLI."""
import sys
from typing import List, Optional

from cliconfig.base import Config
from cliconfig.cli_parser import parse_cli
from cliconfig.dict_routines import flatten, show_dict, unflatten
from cliconfig.process_routines import (
    load_processing,
    merge_flat_paths_processing,
    merge_flat_processing,
    save_processing,
)
from cliconfig.processing.base import Processing
from cliconfig.processing.builtin import DefaultProcessings
from cliconfig.tag_routines import clean_all_tags


def make_config(
    *default_config_paths: str,
    process_list: Optional[List[Processing]] = None,
    add_default_processing: bool = True,
) -> Config:
    r"""Make a config from default configs and CLI arguments and apply processing.

    It uses the CLI Config routines to parse the CLI arguments and merge
    them in a simple way. Apply the processing functions on each merge.

    Parameters
    ----------
    default_config_paths : Tuple[str]
        Paths to default configs. They are merged in order and new keys
        are allowed.
    process_list: Optional[List[Processing]], optional
        The list of processing to apply during each merge. None for empty list.
        By default None.
        If add_default_processing is True, the default processing
        (in :mod:`cliconfig.processing.builtin`) are added to the list.
    add_default_processing : bool, optional
        If True, add the default processing (in :mod:`cliconfig.processing.builtin`)
        to the processing list.

    Raises
    ------
    ValueError
        If allow_new_keys is False and CLI has new keys that are not
        in default configs.

    Returns
    -------
    config : Config
        The built config. Contains the config dict (config.dict) and the processing
        list (config.process_list), which can be used to apply further processing
        routines.

    Examples
    --------
    ::

        # main.py
        config = make_config('data.yaml', 'model.yaml', 'train.yaml')

    .. code-block:: text

        python main.py -- config bestmodel.yaml,mydata.yaml \
            --architecture.layers.hidden_dim=64

    """
    # Create the processing list
    if process_list is None:
        process_list_: List[Processing] = []
    if add_default_processing:
        process_list_ += DefaultProcessings().list

    config = Config({}, process_list_)

    # Merge default configs and additional configs
    additional_config_paths, cli_params_dict = parse_cli(sys.argv)
    for i, paths in enumerate([default_config_paths, additional_config_paths]):
        # Allow new keys for default configs only
        allow_new_keys = i == 0
        for path in paths:
            config = merge_flat_paths_processing(
                config,
                path,
                allow_new_keys=allow_new_keys,
                preprocess_first=False,  # Already processed
            )

    # Allow new keys for CLI parameters but do not merge them and raise
    # warning.
    cli_params_dict = flatten(cli_params_dict)
    new_keys, keys = [], list(cli_params_dict.keys())
    for key in keys:
        if clean_all_tags(key) not in config.dict:
            # New key: delete it
            new_keys.append(clean_all_tags(key))
            del cli_params_dict[key]
    if new_keys:
        new_keys_message = "  - " + "\n  - ".join(new_keys)
        print(
            "[CONFIG] Warning: New keys found in CLI parameters "
            f"that will not be merged:\n{new_keys_message}"
        )
    # Merge CLI parameters
    cli_params_config = Config(cli_params_dict, [])
    config = merge_flat_processing(
        config,
        cli_params_config,
        allow_new_keys=False,
        preprocess_first=False
    )
    print(
        f"[CONFIG] Info: Merged {len(default_config_paths)} default config(s), "
        f"{len(additional_config_paths)} additional config(s) and "
        f"{len(cli_params_dict)} CLI parameter(s)."
    )
    # Unflatten the config dict
    config.dict = unflatten(config.dict)
    return config


def load_config(
    path: str,
    default_config_paths: Optional[List[str]] = None,
    process_list: Optional[List[Processing]] = None,
    *,
    add_default_processing: bool = True,
) -> Config:
    """Load config from a file and merge into optional default configs.

    First merge the default configs together, then load the default config,
    apply the post-load processing, and finally merge the loaded config

    Parameters
    ----------
    path : str
        The path to the file to load the configuration.
    default_config_paths : Optional[List[str]], optional
        Paths to default configs. They are merged in order, new keys are allowed.
        Then, the loaded config is merged into the result. None for no default configs.
        By default None.
    process_list: Optional[List[Processing]]
        The list of processing to apply after loading. Only postload
        method is applied. The order of the processing is given
        by the postload_order attribute of the processing.
        If None, no processing is applied. By default None.
    add_default_processing : bool, optional
        If True, add the default processing to the processing list.

    Returns
    -------
    config: Dict[str, Any]
        The loaded config. Contains the config dict (config.dict) and the processing
        list (config.process_list), which can be used to apply further processing
        routines.
    """
    # Crate process_list
    if process_list is None:
        process_list_ = []
    if add_default_processing:
        process_list_ += DefaultProcessings().list

    config = Config({}, process_list_)
    if default_config_paths:
        for config_path in default_config_paths:
            config = merge_flat_paths_processing(
                config,
                config_path,
                allow_new_keys=True,
                preprocess_first=False,  # Already processed
            )
    # Disallow new keys for loaded config
    loaded_config = load_processing(path, config.process_list)
    # Update the config list from loaded_config in config
    config.process_list = loaded_config.process_list
    # Merge the loaded config into the config
    # NOTE: The loaded config is processed with pre-merge so that tags in
    # the yaml files are correctly processed.
    config = merge_flat_processing(
        config,
        loaded_config,
        allow_new_keys=False,
        preprocess_first=False,
    )
    # Unflatten the config
    config.dict = unflatten(config.dict)
    return config


def save_config(config: Config, path: str) -> None:
    """Save a config and apply pre-save processing before saving.

    Parameters
    ----------
    config : Dict[str, Any]
        The config to save.
    path : str
        The path to the yaml file to save the dict.
    """
    save_processing(config, path)


def show_config(config: Config, start_indent: int = 1) -> None:
    """Show the config dict in a pretty way.

    The config dict is unflattened before.

    Parameters
    ----------
    config : Config
        The config to show.
    start_indent : int, optional
        The number of starting tab indent (4 spaces), by default 1.
    """
    show_dict(config.dict, start_indent)
