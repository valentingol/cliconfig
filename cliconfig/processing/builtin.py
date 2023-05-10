"""Built-in processing classes.

Classes to apply pre-merge, post-merge, pre-save and post-load modifications
to dict with processing routines (found in cliconfig.process_routines).
"""
# pylint: disable=unused-argument
from typing import Any, Dict

from cliconfig.process_routines import (
    merge_flat_paths_processing,
    merge_flat_processing,
)
from cliconfig.processing._type_parser import _parse_type
from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_all_tags, clean_tag


class ProcessMerge(Processing):
    """Merge dicts just in time with '@merge_after/_before/_add' tags.

    Tag your key with '@merge_after', '@merge_before' or @merge_add to load
    the dict corresponding to the value (path) and merge it just before or after
    the current dict.

    * '@merge_add' merges the dict corresponding to the path by allowing ONLY new keys
      It is a security check when you want to add a dict completely new
      It is a typical usage for a default config splitted in several files.
    * '@merge_after' merge the dict corresponding to the path on the current dict
    * '@merge_before' merge the current dict on the dict corresponding to the path

    The processing is a pre-merge processing only and occurs before
    most of the other processing.
    Pre-merge order: -20.0

    Examples
    --------
    .. code-block:: yaml

        --- # config1.yaml
        a:
          b: 1
          b_path@merge_after: dict2.yaml
        --- # config2.yaml
        a.b: 2
        c_path@merge_add: config3.yaml
        --- # config3.yaml
        c: 3

    Before merging, the config1 is interpreted as the dict:

    .. code-block:: python

        {'a': {'b': 2, 'b_path': 'config2.yaml'}, 'c_path': 'config3.yaml', 'c': 3}`

    If you replace '@merge_after' by '@merge_before', it will be:

    .. code-block:: python

        {'a': {'b': 1, 'b_path': 'config2.yaml'}, 'c_path': 'config3.yaml', 'c': 3}`

    Finally, if you replace '@merge_after' by '@merge_add', it will raises an
    error because the key 'a.b' already exists in the dict.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = -20.0

    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, val in items:
            end_key = flat_key.split('.')[-1]
            if "@merge_after" in end_key:
                if not isinstance(val, str) or not val.endswith('.yaml'):
                    raise ValueError(
                        "Key with '@merge_after' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                del flat_dict[flat_key]
                flat_dict[clean_tag(flat_key, 'merge_after')] = val
                # Merge + process the dicts
                # NOTE: we allow new keys with security because the merge
                # following this pre-merge will avoid the creation of
                # new keys if needed.
                flat_dict = merge_flat_paths_processing(
                    flat_dict,
                    val,
                    processing_list=processing_list,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                )
            elif "@merge_before" in end_key:
                if not isinstance(val, str) or not val.endswith('.yaml'):
                    raise ValueError(
                        "Key with '@merge_before' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                del flat_dict[flat_key]
                flat_dict[clean_tag(flat_key, 'merge_before')] = val
                # Merge + process the dicts
                flat_dict = merge_flat_paths_processing(
                    val,
                    flat_dict,
                    processing_list=processing_list,
                    allow_new_keys=True,
                    preprocess_second=False,  # Already processed
                )
            elif "@merge_add" in end_key:
                if not isinstance(val, str) or not val.endswith('.yaml'):
                    raise ValueError(
                        "Key with '@merge_add' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                del flat_dict[flat_key]
                flat_dict[clean_tag(flat_key, 'merge_add')] = val
                # Pre-merge process the dict
                flat_dict_to_merge = merge_flat_paths_processing(
                    {},
                    val,
                    processing_list=processing_list,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                    postprocess=False,
                )
                for key in flat_dict_to_merge:
                    if key in flat_dict:
                        raise ValueError(
                            f"@merge_add doest not allow to add already "
                            f"existing keys but key '{key}' is found in both "
                            "dicts. Use @merge_after or @merge_before if you "
                            "want to merge this key, or check your key names."
                        )
                # Merge the dicts (order is not important by construction)
                flat_dict = merge_flat_processing(
                    flat_dict,
                    flat_dict_to_merge,
                    processing_list=processing_list,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                    preprocess_second=False,  # Already processed
                    postprocess=True,
                )
        return flat_dict


class ProcessCopy(Processing):
    """Copy a value with '@copy' tag.

    Tag your key with '@copy' and with value the name of the flat key to copy.
    This processing is a pre-merge processing only and occurs after most of
    the other pre-merge processing.
    Pre-merge order: 10.0

    Examples
    --------
    .. code-block:: yaml

        # config.yaml
        a:
          b: 1
          c@copy: a.b

    Before merging, the config is interpreted as the dict

    .. code-block:: python

        {'a': {'b': 1, 'c': 1}}
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 10.0

    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, val in items:
            key = flat_key.split(".")[-1]
            if "@copy" in key:
                if not isinstance(val, str) or val not in flat_dict:
                    raise ValueError(
                        "Key with '@copy' tag must be associated "
                        "to a string corresponding to an existing flat key. "
                        f"The problem occurs at key: {flat_key} with value: {val}"
                    )
                # Remove the tag and update the dict
                flat_dict[clean_tag(flat_key, "copy")] = flat_dict[val]
                del flat_dict[flat_key]
        return flat_dict


class ProcessTyping(Processing):
    """Force a type with '@type:mytype' tag. The type is preserved forever.

    Allow basic types (none, any, bool, int, float, str, list, dict), nested lists,
    nested dicts, unions (with Union or the '|' symbol) and Optional.
    It checks and store the type in premerge and check alls forced types on postmerge.
    It always occurs last in premerge and postmerge.
    Pre-merge order: 20.0
    Post-merge order: 20.0
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 20.0
        self.postmerge_order = 20.0
        self.forced_types: Dict[str, tuple] = {}
        self.type_desc: Dict[str, str] = {}  # For error messages

    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa: ARG002
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, val in items:
            end_key = flat_key.split('.')[-1]
            if "@type:" in end_key:
                # Get the type description
                trail = end_key.split("@type:")[-1]
                type_desc = trail.split('@')[0]  # (in case of multiple tags)
                expected_type = tuple(_parse_type(type_desc))
                clean_key = clean_all_tags(flat_key)
                if (clean_key in self.forced_types
                        and set(self.forced_types[clean_key]) != set(expected_type)):
                    raise ValueError(
                        f"Find the tag '@type:{type_desc}' on a key that has already "
                        "been associated to an other type: "
                        f"{self.type_desc[clean_key]}. "
                        f"Find problem at key: {flat_key}"
                    )
                if not isinstance(val, expected_type):
                    raise ValueError(
                        f"Key with '@type:{type_desc}' tag must be associated "
                        f"to a value of type {type_desc}. Find the value: {val} "
                        f"at key: {flat_key}"
                    )
                # Remove the tag
                del flat_dict[flat_key]
                flat_dict[clean_tag(flat_key, f'type:{type_desc}')] = val
                # Add the forced type
                self.forced_types[clean_key] = expected_type
                self.type_desc[clean_key] = type_desc
        return flat_dict

    def postmerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa: ARG002
    ) -> Dict[str, Any]:
        """Post-merge processing."""
        for key, expected_type in self.forced_types.items():
            if key in flat_dict and not isinstance(flat_dict[key], expected_type):
                type_desc = self.type_desc[key]
                raise ValueError(
                    f"Key previously tagged with '@type:{type_desc}' must be "
                    f"associated to a value of type {type_desc}. Find the "
                    f"value: {flat_dict[key]} of type {type(flat_dict[key])} "
                    f"at key: {key}"
                )
        return flat_dict
