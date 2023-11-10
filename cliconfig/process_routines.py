"""Routines to manipulate dictionaries with processing.

Used by :mod:`.config_routines`.
"""
from typing import List, Optional, Union

from cliconfig.base import Config
from cliconfig.dict_routines import (
    _flat_before_merge,
    flatten,
    load_dict,
    merge_flat,
    save_dict,
    unflatten,
)
from cliconfig.processing.base import Processing


def merge_flat_processing(
    config1: Config,
    config2: Config,
    *,
    allow_new_keys: bool = True,
    preprocess_first: bool = True,
    preprocess_second: bool = True,
    postprocess: bool = True,
) -> Config:
    """Flatten, merge config2 into config1 and apply pre and post processing.

    Work even if the config dicts have a mix of nested and flat dictionaries.
    If both arguments are configs, the process lists are merged before applying
    the processing. The duplicate processings (with same internal variables)
    are removed.

    Parameters
    ----------
    config1 : Config
        The first config.
    config2 : Config
        The second dict to merge into config1.
    allow_new_keys : bool, optional
        If True, new keys (that are not in config1) are allowed in config2.
        Otherwise, it raises an error. By default True.
    preprocess_first : bool, optional
        If True, apply pre-merge processing to config1. By default True.
    preprocess_second : bool, optional
        If True, apply pre-merge processing to config2. By default True.
    postprocess : bool, optional
        If True, apply post-merge processing to the merged config. By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and config2 has new keys that are not in config1.
    ValueError
        If there are conflicting keys when flatten one of the dicts.

    Returns
    -------
    flat_config : Config
        The merged flat config.
    """
    # Flatten the dictionaries
    config1.dict, config2.dict = _flat_before_merge(config1.dict, config2.dict)
    # Get the process list of the merge
    process_list = config1.process_list
    for process in config2.process_list:
        # NOTE 2 processings are equal if they are the same class and add the same
        # attributes.
        if process not in process_list:
            process_list.append(process)
    # Apply the pre-merge processing
    if preprocess_first:
        config1.process_list = process_list
        pre_order_list = sorted(process_list, key=lambda x: x.premerge_order)
        for processing in pre_order_list:
            config1 = processing.premerge(config1)
        process_list = config1.process_list
    if preprocess_second:
        config2.process_list = process_list
        pre_order_list = sorted(process_list, key=lambda x: x.premerge_order)
        for processing in pre_order_list:
            config2 = processing.premerge(config2)
        process_list = config2.process_list
    # Merge the dictionaries
    flat_dict = merge_flat(config1.dict, config2.dict, allow_new_keys=allow_new_keys)
    # Create the new config
    flat_config = Config(flat_dict, process_list)
    # Apply the postmerge processing
    if postprocess:
        post_order_list = sorted(process_list, key=lambda x: x.postmerge_order)
        for processing in post_order_list:
            flat_config = processing.postmerge(flat_config)
    return flat_config


def merge_flat_paths_processing(
    config_or_path1: Union[str, Config],
    config_or_path2: Union[str, Config],
    *,
    additional_process: Optional[List[Processing]] = None,
    allow_new_keys: bool = True,
    preprocess_first: bool = True,
    preprocess_second: bool = True,
    postprocess: bool = True,
) -> Config:
    """Flatten, merge and apply processing to two configs or their yaml paths.

    Similar to :func:`merge_flat_processing` but allows to pass configs
    or their yaml paths. Work even if the configs have a mix of nested and flat dicts.
    If both arguments are configs, the process lists are merged before applying
    the processing. The duplicate processings (with same internal variables)
    are removed.

    Parameters
    ----------
    config_or_path1 : Union[str, Config]
        The first config or its path.
    config_or_path2 : Union[str, Config]
        The second config or its path, to merge into first config.
    additional_process : Optional[List[Processing]], optional
        Additional processings to apply to the merged config. It can
        be useful to merge a config from its path while it has some specific
        processings.
    allow_new_keys : bool, optional
        If True, new keys (that are not in config1) are allowed in config2.
        Otherwise, it raises an error. By default True.
    preprocess_first : bool, optional
        If True, apply pre-merge processing to config1. By default True.
    preprocess_second : bool, optional
        If True, apply pre-merge processing to config2. By default True.
    postprocess : bool, optional
        If True, apply post-merge processing to the merged config. By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and config2 has new keys that are not in config1.
    ValueError
        If there are conflicting keys when flatten one of the dicts.

    Returns
    -------
    flat_config : Config
        The merged flat config.
    """
    configs = []
    for config_or_path in [config_or_path1, config_or_path2]:
        if isinstance(config_or_path, str):
            config_dict = load_dict(config_or_path)
            config = Config(config_dict, [])
        elif isinstance(config_or_path, Config):
            config = config_or_path
        elif isinstance(config_or_path, dict):
            raise ValueError(
                "config_or_path must be a Config instance or a path to a yaml file "
                "but you passed a dict. If you want to use it as a valid input, "
                "you should use Config(<input dict>, []) instead."
            )
        else:
            raise ValueError(
                "config_or_path must be a Config instance or a path to a yaml file."
            )
        configs.append(config)
    config1, config2 = configs[0], configs[1]
    if additional_process is not None:
        config1.process_list.extend(additional_process)
        config2.process_list.extend(additional_process)
    flat_config = merge_flat_processing(
        config1,
        config2,
        allow_new_keys=allow_new_keys,
        preprocess_first=preprocess_first,
        preprocess_second=preprocess_second,
        postprocess=postprocess,
    )
    return flat_config


def save_processing(config: Config, path: str) -> None:
    """Save a config and apply pre-save processing before saving.

    Parameters
    ----------
    config : Config
        The config to save.
    path : str
        The path to the yaml file to save the config dict.
    """
    config_to_save = Config(flatten(config.dict), config.process_list)
    # Get the pre-save order
    order_list = sorted(config.process_list, key=lambda x: x.presave_order)
    # Apply the pre-save processing
    for processing in order_list:
        config_to_save = processing.presave(config_to_save)
    # Unflatten and save the dict
    config_to_save.dict = unflatten(config_to_save.dict)
    save_dict(config_to_save.dict, path)


def load_processing(path: str, process_list: List[Processing]) -> Config:
    """Load a dict from yaml file path and apply post-load processing.

    Parameters
    ----------
    path : str
        The path to the file to load the dict.
    process_list: List[Processing]
        The list of processing to apply after loading. Only post-load
        processing is applied. The order of the processing is given
        by the postload_order attribute of the processing.

    Returns
    -------
    flat_config : Config
        The loaded flat config.
    """
    # Load the dict and flatten it
    out_dict = flatten(load_dict(path))
    flat_config = Config(out_dict, process_list)
    # Get the post-load order
    order_list = sorted(process_list, key=lambda x: x.postload_order)
    # Apply the post-load processing
    for processing in order_list:
        flat_config = processing.postload(flat_config)
    return flat_config


def end_build_processing(flat_config: Config) -> Config:
    """Apply end-build processings to a flat config.

    Parameters
    ----------
    flat_config : Config
        The flat config to apply the end-build processings.

    Returns
    -------
    flat_config : Config
        The flat config after applying the end-build processings.
    """
    order_list = sorted(flat_config.process_list, key=lambda x: x.endbuild_order)
    for processing in order_list:
        flat_config = processing.endbuild(flat_config)
    return flat_config
