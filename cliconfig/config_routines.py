"""Functions to manipulate config as dict with yaml files and CLI."""
import sys
from typing import Any, Dict, List, Optional

from cliconfig.base import Config
from cliconfig.cli_parser import parse_cli
from cliconfig.dict_routines import flatten, show_dict, unflatten
from cliconfig.process_routines import (
    end_build_processing,
    load_processing,
    merge_flat_paths_processing,
    merge_flat_processing,
    save_processing,
)
from cliconfig.processing.base import Processing
from cliconfig.processing.builtin import DefaultProcessings
from cliconfig.tag_routines import clean_all_tags, is_tag_in


def make_config(
    *default_config_paths: str,
    process_list: Optional[List[Processing]] = None,
    add_default_processing: bool = True,
    fallback: str = "",
    no_cli: bool = False,
) -> Config:
    r"""Make a config from default config(s) and CLI argument(s) with processing.

    The function uses the CLI Config routines :func:`.parse_cli` to parse the CLI
    arguments and merge them with :func:`.merge_flat_paths_processing`, applying
    the pre-merge and post-merge processing functions on each merge.

    Parameters
    ----------
    default_config_paths : Tuple[str]
        Paths to default configs. They are merged in order and new keys
        are allowed.
    process_list: Optional[List[Processing]], optional
        The list of processing to apply during each merge. None for empty list.
        By default None.
    add_default_processing : bool, optional
        If add_default_processing is True, the default processings
        (found on :class:`.DefaultProcessings`) are added to the list of
        processings. By default True.
    fallback : str, optional
        Path of the configuration to use if no additional config is provided
        with ``--config``. No fallback config if empty string (default),
        in that case, the config is the default configs plus the CLI arguments.
    no_cli : bool, optional
        If True, the CLI arguments are not parsed and the config is only
        built from the default_config_paths in input and the
        fallback argument is ignored. By default False.

    Raises
    ------
    ValueError
        If additional configs have new keys that are not in default configs.

    Returns
    -------
    config : Config
        The nested built config. Contains the config dict (config.dict) and
        the processing list (config.process_list) which can be used to apply
        further processing routines.

    Note
    ----

        Setting additional arguments from CLI that are not in default configs
        does NOT raise an error but only a warning. This ensures the compatibility
        with other CLI usage (e.g notebook, argparse, etc.)

    Examples
    --------
    ::

        # main.py
        config = make_config('data.yaml', 'model.yaml', 'train.yaml')

    .. code-block:: text

        $ python main.py -- config [bestmodel.yaml,mydata.yaml] \
              --architecture.layers.hidden_dim=64

    """
    # Create the processing list
    process_list_: List[Processing] = [] if process_list is None else process_list
    if add_default_processing:
        process_list_ += DefaultProcessings().list
    config = Config({}, process_list_)
    if no_cli:
        additional_config_paths: List[str] = []
        cli_params_dict: Dict[str, Any] = {}
    else:
        additional_config_paths, cli_params_dict = parse_cli(sys.argv)
        if not additional_config_paths and fallback:
            # Add fallback config
            additional_config_paths = [fallback]
    # Merge default configs and additional configs
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
        if (
            not is_tag_in(key, "new", full_key=True)
            and clean_all_tags(key) not in config.dict
        ):
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
        config, cli_params_config, allow_new_keys=False, preprocess_first=False
    )
    print(
        f"[CONFIG] Info: Merged {len(default_config_paths)} default config(s), "
        f"{len(additional_config_paths)} additional config(s) and "
        f"{len(cli_params_dict)} CLI parameter(s)."
    )
    # Apply end-build processing
    config = end_build_processing(config)
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

    First merge the default configs together (if any), then load the config
    from path, apply the post-load processing, and finally merge the loaded
    config.

    Parameters
    ----------
    path : str
        The path to the file to load the configuration.
    default_config_paths : Optional[List[str]], optional
        Paths to default configs. They are merged in order, new keys are allowed.
        Then, the loaded config is merged into the result. None for no default configs.
        By default None.
    process_list: Optional[List[Processing]]
        The list of processing to apply after loading and for the merges.
        If None, no processing is applied. By default None.
    add_default_processing : bool, optional
        If add_default_processing is True, the default processings
        (found on :class:`.DefaultProcessings`) are added to the list of
        processings. By default True.

    Returns
    -------
    config: Dict[str, Any]
        The nested loaded config. Contains the config dict (config.dict) and
        the processing list (config.process_list) which can be used to apply
        further processing routines.

    Note
    ----

        If default configs are provided, the function does not allow new keys
        for the loaded config. This is for helping the user to see how to
        adapt the config file if the default configs have changed.
    """
    # Crate process_list
    process_list_: List[Processing] = [] if process_list is None else process_list
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
    loaded_config = load_processing(path, config.process_list)
    # Update the config list from loaded_config in config
    config.process_list = loaded_config.process_list
    # Merge the loaded config into the config and
    # disallow new keys for loaded config
    # if default configs are provided
    config = merge_flat_processing(
        config,
        loaded_config,
        allow_new_keys=default_config_paths is None,
        preprocess_first=False,
    )
    # Apply end-build processing
    config = end_build_processing(config)
    # Unflatten the config
    config.dict = unflatten(config.dict)
    return config


def save_config(config: Config, path: str) -> None:
    """Save a config and apply pre-save processing before saving.

    Alias for :func:`.save_processing`.

    Parameters
    ----------
    config : Dict[str, Any]
        The config to save.
    path : str
        The path to the yaml file to save the dict.
    """
    save_processing(config, path)


def show_config(config: Config) -> None:
    """Show the config dict in a pretty way.

    The config dict is automatically unflattened before printing.

    Parameters
    ----------
    config : Config
        The config to show.
    """
    print("Config:")
    show_dict(config.dict, start_indent=1)


def flatten_config(config: Config) -> Config:
    """Flatten a config.

    Parameters
    ----------
    config : Config
        The config to flatten.

    Returns
    -------
    confg : Config
        The config containing a flattened dict.
    """
    config.dict = flatten(config.dict)
    return config


def unflatten_config(config: Config) -> Config:
    """Unflatten a config.

    Parameters
    ----------
    config : Config
        The config to unflatten.

    Returns
    -------
    config : Config
        The config containing an unflattened dict.
    """
    config.dict = unflatten(config.dict)
    return config


def update_config(config: Config, new_dict: dict) -> Config:
    """Update a config with a new dict without triggering processing.

    The resulting config is unflattened.

    Parameters
    ----------
    config : Config
        The config to update.
    new_dict : dict
        The dict to update the config with.

    Returns
    -------
    config : Config
        The updated config.
    """
    config.dict = flatten(config.dict)
    config.dict.update(flatten(new_dict))
    config.dict = unflatten(config.dict)
    return config
