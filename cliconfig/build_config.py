"""Functions to manipulate config as dict with yaml files and CLI."""
import sys
from typing import Any, Dict, List, Optional

from cliconfig.cli_parser import parse_cli
from cliconfig.dict_routines import unflatten
from cliconfig.process_routines import (
    load_processing,
    merge_flat_paths_processing,
    merge_flat_processing,
)
from cliconfig.processing.base import Processing


def make_config(
    *default_config_paths: str,
    processing_list: Optional[List[Processing]] = None,
) -> Dict[str, Any]:
    r"""Make a config from default configs and CLI arguments and apply processing.

    It uses the CLI Config routines to parse the CLI arguments and merge
    them in a simple way. Apply the processing functions on each merge.

    Parameters
    ----------
    default_config_paths : Tuple[str]
        Paths to default configs. They are merged in order and new keys
        are allowed.
    processing_list: Optional[List[Processing]], optional
        The list of processing to apply during each merge. Only premerge and
        postmerge methods are applied. The order of the processing is given
        by the premerge_order and postmerge_order attributes of the processing.
        If None, no processing is applied. By default None.

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

    if processing_list is None:
        processing_list = []

    for default_config_path in default_config_paths:
        # Allow new keys for default configs
        config = merge_flat_paths_processing(
            config,
            default_config_path,
            processing_list,
            allow_new_keys=True,
            preprocess_first=False,  # Already processed
        )

    for config_path in config_paths:
        # Disallow new keys for additional configs
        config = merge_flat_paths_processing(
            config,
            config_path,
            processing_list,
            allow_new_keys=False,
            preprocess_first=False,
        )
    # Disallow new keys for CLI parameters
    config = merge_flat_processing(
        config,
        config_cli_params,
        processing_list,
        allow_new_keys=False,
        preprocess_first=False)
    # Unflatten the config
    config = unflatten(config)
    return config


def load_config(
    path: str,
    default_config_paths: Optional[List[str]] = None,
    processing_list: Optional[List[Processing]] = None,
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
    processing_list: Optional[List[Processing]]
        The list of processing to apply after loading. Only postload
        method is applied. The order of the processing is given
        by the postload_order attribute of the processing.
        If None, no processing is applied. By default None.

    Returns
    -------
    config: Dict[str, Any]
        The loaded config.
    """
    if processing_list is None:
        processing_list = []
    config: Dict[str, Any] = {}
    if default_config_paths:
        for config_path in default_config_paths:
            config = merge_flat_paths_processing(
                config,
                config_path,
                processing_list=processing_list,
                allow_new_keys=True,
                preprocess_first=False,  # Already processed
            )
    # Disallow new keys for loaded config
    loaded_config = load_processing(path, processing_list)
    config = merge_flat_processing(
        config,
        loaded_config,
        processing_list=processing_list,
        allow_new_keys=False,
        preprocess_first=False,
    )
    # Unflatten the config
    config = unflatten(config)
    return config
