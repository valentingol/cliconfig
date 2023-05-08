"""Example of useful processing classes.

Classes to apply pre-merge, post-merge, pre-save and post-load modifications
to dict with processing routines (found in cliconfig.process_routines).
"""
from typing import Any, Dict

from cliconfig.process_routines import Processing, merge_flat_paths_processing


class ProcessMerge(Processing):
    """Merge dict just in time with '@merge_after' and '@merge_before' tags.

    Tag your key with '@merge_after' or '@merge_before' to load the dict
    corresponding to a path and merge it just before or after the current
    dicturation. The processing is a pre-merge processing only and occurs before
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

    Before merging, the config1 is interpreted as the dict
    `{'a': {'b': 2, 'b_path': 'config2.yaml'}` If you replace '@merge_after'
    by '@merge_before', it will be `{'a': {'b': 1, 'b_path': 'config2.yaml'}`
    instead.
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
            if flat_key.endswith('@merge_after'):
                # NOTE: we allow new keys here fore more flexibility but we note that
                # the merge following this pre-merge will avoid the creation of
                # new keys if needed.
                if not isinstance(val, str) or not val.endswith('.yaml'):
                    raise ValueError(
                        "Key with '@merge_after' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                flat_dict[flat_key[:-len('@merge_after')]] = val
                del flat_dict[flat_key]
                # Merge + process the dicts
                flat_dict = merge_flat_paths_processing(
                    flat_dict,
                    val,
                    processing_list=processing_list,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                )
            if flat_key.endswith('@merge_before'):
                # NOTE: we allow new keys here fore more flexibility but we note that
                # the merge following this pre-merge will avoid the creation of
                # new keys if needed.
                if not isinstance(val, str) or not val.endswith('.yaml'):
                    raise ValueError(
                        "Key with '@merge_before' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the key
                flat_dict[flat_key[:-len('@merge_before')]] = val
                del flat_dict[flat_key]
                # Merge + process the dicts
                flat_dict = merge_flat_paths_processing(
                    val,
                    flat_dict,
                    processing_list=processing_list,
                    allow_new_keys=True,
                    preprocess_second=False,  # Already processed
                )
        return flat_dict


class ProcessCopy(Processing):
    """Copy a value with '@copy' tag.

    Tag your key with '@copy' and with value the name of the flat key to copy.
    This processing is a pre-merge processing only and occurs after most of
    the other pre-merge processing.
    Pre-merge order: 20.0

    Examples
    --------
    .. code-block:: yaml

        # config.yaml
        a:
          b: 1
          c@copy: a.b

    Before merging, the config is interpreted as the dict
    `{'a': {'b': 1, 'c': 1}}`.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 20.0

    # pylint: disable=unused-argument
    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, val in items:
            if flat_key.endswith('@copy'):
                if not isinstance(val, str):
                    raise ValueError(
                        "Key with '@copy' tag must be associated "
                        "to a string corresponding to a flat key."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag and update the dict
                flat_dict[flat_key[:-len('@copy')]] = flat_dict[val]
                del flat_dict[flat_key]
        return flat_dict


class ProcessProtect(Processing):
    """Make a value protected with '@protect' tag.

    The protected value cannot be changed on merge as long as this processing
    is used. Otherwise, it raises an error. This processing store protected
    keys and values and remove the '@protect' tag. It always occurs before anything
    else on pre-merge processing and after everything else on post-merge.
    Pre-merge order: -40.0
    Post-merge order: 40.0
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = -40.0
        self.postmerge_order = 40.0
        self.protected_dict: Dict[str, Any] = {}

    # pylint: disable=unused-argument
    def premerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Pre-merge processing."""
        items = list(flat_dict.items())
        for flat_key, val in items:
            if flat_key.endswith('@protect'):
                new_key = flat_key[:-len('@protect')]
                if new_key in flat_dict and self.protected_dict[new_key] != val:
                    raise ValueError(
                        f"Attempt to change a protected key (tagged by '@protect'): "
                        f"{new_key}. Protected value: {self.protected_dict[new_key]}, "
                        f"new value: {val}."
                    )
                # Remove the tag in the key
                flat_dict[new_key] = val
                del flat_dict[flat_key]
                # Store the protected key and value
                self.protected_dict[flat_key[:-len('@protect')]] = val
        return flat_dict

    # pylint: disable=unused-argument
    def postmerge(
        self,
        flat_dict: Dict[str, Any],
        processing_list: list,  # noqa
    ) -> Dict[str, Any]:
        """Post-merge processing."""
        for key, val in self.protected_dict.items():
            if key not in flat_dict:
                raise ValueError(
                    f"Protected key (tagged by '@protect') {key} has been removed "
                    f"after merge. Protected value: {val}, new value: nothing."
                )

            if flat_dict[key] != val:
                raise ValueError(
                    f"Protected key (tagged by '@protect') {key} has been changed "
                    f"after merge. Protected value: {val}, new value: {flat_dict[key]}."
                )
        return flat_dict
