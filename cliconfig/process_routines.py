"""Routines to manipulate dictionaries with processing."""
from typing import Any, Dict, List, Tuple, Union

from cliconfig.dict_routines import _flat_before_merge, load_dict, merge_flat, save_dict
from cliconfig.processing.base import Processing


def merge_flat_processing(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    processing_list: List[Processing],
    *,
    allow_new_keys: bool = True,
    preprocess_first: bool = True,
    preprocess_second: bool = True,
    postprocess: bool = True,
) -> Tuple[Dict[str, Any], List[Processing]]:
    """Flatten, merge dict2 into dict1 and apply pre and post processing.

    Similar to :func:`cliconfig.dict_routines.merge_flat` but with processing
    applied before and/or after the merge. Work even if the dicts have
    a mix of nested and flat dictionaries.

    Parameters
    ----------
    dict1 : Dict[str, Any]
        The first dict. It can be nested, flat or a mix of both.
    dict2 : Dict[str, Any]
        The second dict to merge into dict1.
    processing_list: List[Processing]
        The list of processing to apply during the merge. Only premerge and
        postmerge methods are applied. The order of the processing is given
        by the premerge_order and postmerge_order attributes of the processing.
    allow_new_keys : bool, optional
        If True, new keys (that are not in dict1) are allowed in dict2.
        By default True.
    preprocess_first : bool, optional
        If True, apply pre*merge processing to dict1. By default True.
    preprocess_second : bool, optional
        If True, apply pre*merge processing to dict2. By default True.
    postprocess : bool, optional
        If True, apply post*merge processing to the merged dict. By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and dict2 has new keys that are not in dict1.
    ValueError
        If there are conflicting keys when flatten one of the dicts.
        See last example. You may consider calling :func:`clean_pre_flat` on the input
        dicts in that case.

    Returns
    -------
    flat_dict : Dict[str, Any]
        The flat dict (all keys are at the root and separated by dots).
    processing_list : List[Processing]
        The updated processing list.
    """
    # Get the pre-merge and post-merge order
    pre_order_list = sorted(processing_list, key=lambda x: x.premerge_order)
    post_order_list = sorted(processing_list, key=lambda x: x.postmerge_order)
    # Flatten the dictionaries
    flat_dict1, flat_dict2 = _flat_before_merge(dict1, dict2)
    # Apply the premerge processing
    for processing in pre_order_list:
        if preprocess_first:
            flat_dict1 = processing.premerge(flat_dict1, processing_list)
            if hasattr(processing, "processing_list"):
                # Get the eventually updated list from attribute
                processing_list = processing.processing_list
        if preprocess_second:
            flat_dict2 = processing.premerge(flat_dict2, processing_list)
            if hasattr(processing, "processing_list"):
                # Get the eventually updated list from attribute
                processing_list = processing.processing_list
    # Merge the dictionaries
    flat_dict = merge_flat(flat_dict1, flat_dict2, allow_new_keys=allow_new_keys)
    # Apply the postmerge processing
    for processing in post_order_list:
        if postprocess:
            flat_dict = processing.postmerge(flat_dict, processing_list)
            if hasattr(processing, "processing_list"):
                # Get the eventually updated list from attribute
                processing_list = processing.processing_list
    return flat_dict, processing_list


def merge_flat_paths_processing(
    dict_or_path1: Union[str, Dict[str, Any]],
    dict_or_path2: Union[str, Dict[str, Any]],
    processing_list: List[Processing],
    *,
    allow_new_keys: bool = True,
    preprocess_first: bool = True,
    preprocess_second: bool = True,
    postprocess: bool = True,
) -> Tuple[Dict[str, Any], List[Processing]]:
    """Flatten, merge and apply processing to two dictionaries or their yaml paths.

    Similar to :func:`cliconfig.dict_routines.merge_flat_paths` but with processing
    applied before and/or after the merge. It is also similar to
    :func:`merge_flat_processing` but allows to pass dictionaries or yaml paths.
    Work even if the dicts have a mix of nested and flat dictionaries.

    Parameters
    ----------
    dict_or_path1 : Union[str, Dict[str, Any]]
        The first dict or its path.
    dict_or_path2 : Union[str, Dict[str, Any]]
        The second dict or its path, to merge into first dict.
    processing_list: List[Processing]
        The list of processing to apply during the merge. Only premerge and
        postmerge methods are applied. The order of the processing is given
        by the premerge_order and postmerge_order attributes of the processing.
    allow_new_keys : bool, optional
        If True, new keys (that are not in dict1) are allowed in dict2.
        By default True.
    preprocess_first : bool, optional
        If True, apply pre-merge processing to dict1. By default True.
    preprocess_second : bool, optional
        If True, apply pre-merge processing to dict2. By default True.
    postprocess : bool, optional
        If True, apply post-merge processing to the merged dict. By default True.

    Raises
    ------
    ValueError
        If allow_new_keys is False and dict2 has new keys that are not in dict1.
    ValueError
        If there are conflicting keys when flatten one of the dicts.
        See last example. You may consider calling :func:`clean_pre_flat` on the input
        dicts in that case.

    Returns
    -------
    flat_dict : Dict[str, Any]
        The flat dict (all keys are at the root and separated by dots).
    processing_list : List[Processing]
        The updated processing list.
    """
    dicts = []
    for dict_or_path in [dict_or_path1, dict_or_path2]:
        if isinstance(dict_or_path, str):
            _dict = load_dict(dict_or_path)
        else:
            _dict = dict_or_path
        dicts.append(_dict)
    dict1, dict2 = dicts[0], dicts[1]
    flat_dict, processing_list = merge_flat_processing(
        dict1,
        dict2,
        processing_list,
        allow_new_keys=allow_new_keys,
        preprocess_first=preprocess_first,
        preprocess_second=preprocess_second,
        postprocess=postprocess,
    )
    return flat_dict, processing_list


def save_processing(
    in_dict: Dict[str, Any],
    path: str,
    processing_list: List[Processing]
) -> None:
    """Save a dict and apply pre-save processing before saving.

    Parameters
    ----------
    in_dict : Dict[str, Any]
        The dict to save.
    path : str
        The path to the yaml file to save the dict.
    processing_list: List[Processing]
        The list of processing to apply before saving. Only presave
        method is applied. The order of the processing is given
        by the presave_order attribute of the processing.
    """
    # Get the pre-save order
    order_list = sorted(processing_list, key=lambda x: x.presave_order)
    # Apply the pre-save processing
    for processing in order_list:
        in_dict = processing.presave(in_dict, processing_list)
    # Save the dict
    save_dict(in_dict, path)


def load_processing(path: str, processing_list: List[Processing]) -> Dict[str, Any]:
    """Load a dict from yaml file and apply post-load processing.

    Parameters
    ----------
    path : str
        The path to the file to load the dict.
    processing_list: List[Processing]
        The list of processing to apply after loading. Only postload
        method is applied. The order of the processing is given
        by the postload_order attribute of the processing.

    Returns
    -------
    out_dict: Dict[str, Any]
        The loaded dict.
    """
    # Get the post-load order
    order_list = sorted(processing_list, key=lambda x: x.postload_order)
    # Load the dict
    out_dict = load_dict(path)
    # Apply the post-load processing
    for processing in order_list:
        out_dict = processing.postload(out_dict, processing_list)
    return out_dict
