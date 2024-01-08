# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Built-in processing classes.

Built-in classes of the default processing used by the config routines
`cliconfig.config_routines.make_config` and `cliconfig.config_routines.load_config`.
"""
import ast
from typing import Any, Dict, List, Set, Tuple

from cliconfig.base import Config
from cliconfig.dict_routines import unflatten
from cliconfig.process_routines import (
    merge_flat_paths_processing,
    merge_flat_processing,
)
from cliconfig.processing._ast_parser import _process_node
from cliconfig.processing._type_parser import _convert_type, _isinstance, _parse_type
from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_all_tags, clean_tag, dict_clean_tags, is_tag_in

TypeSplitDict = Dict[str, List[Tuple[str, Any]]]


class ProcessMerge(Processing):
    """Merge dicts just in time with `@merge_after/_before/_add` tags.

    Tag your key with `@merge_after`, `@merge_before` or `@merge_add`
    to load the config corresponding to the value (which must be a yaml path) and
    merge it just before or after the current config. The merging process
    allows the config files to make references to each other (typically for copy)
    even without containing the merge tags itself.

    * '@merge_add' merges the dict corresponding to the path by allowing ONLY new keys
      It is a security check when you want to add a dict completely new,
      the typical usage for a default config splitted in several files.
    * '@merge_after' merge the dict corresponding to the path on the current dict
    * '@merge_before' merge the current dict on the dict corresponding to the path

    The processing is a pre-merge processing only and occurs before
    almost all of the other processings.
    Pre-merge order: -20.0

    Examples
    --------
    ```yaml
    # config1.yaml
    a:
        b: 1
        b_path@merge_after: dict2.yaml

    # config2.yaml
    a.b: 2
    c_path@merge_add: config3.yaml

    # config3.yaml
    c: 3
    ```

    Before merging, the config1 is interpreted as the dict:

    ```python
    {'a': {'b': 2, 'b_path': 'config2.yaml'}, 'c_path': 'config3.yaml', 'c': 3}
    ```

    If you replace '@merge_after' by '@merge_before', it will be:

    ```python
    {'a': {'b': 1, 'b_path': 'config2.yaml'}, 'c_path': 'config3.yaml', 'c': 3}
    ```

    Finally, if you replace `@merge_after` by `@merge_add`, it will raise an
    error because the key `a.b` already exists in the dict.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = -20.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, val in items:
            if is_tag_in(flat_key, "merge_after"):
                if not isinstance(val, str) or not val.endswith(".yaml"):
                    raise ValueError(
                        "Key with '@merge_after' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                del flat_config.dict[flat_key]
                flat_config.dict[clean_tag(flat_key, "merge_after")] = val
                # Merge + process the dicts
                # NOTE: we allow new keys with security because the merge
                # following this pre-merge will avoid the creation of
                # new keys if needed.
                flat_config = merge_flat_paths_processing(
                    flat_config,
                    val,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                    postprocess=False,
                )

            elif is_tag_in(flat_key, "merge_before"):
                if not isinstance(val, str) or not val.endswith(".yaml"):
                    raise ValueError(
                        "Key with '@merge_before' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                del flat_config.dict[flat_key]
                flat_config.dict[clean_tag(flat_key, "merge_before")] = val
                # Merge + process the dicts
                flat_config = merge_flat_paths_processing(
                    val,
                    flat_config,
                    allow_new_keys=True,
                    preprocess_second=False,  # Already processed
                    postprocess=False,
                )

            elif is_tag_in(flat_key, "merge_add"):
                if not isinstance(val, str) or not val.endswith(".yaml"):
                    raise ValueError(
                        "Key with '@merge_add' tag must be associated "
                        "to a string corresponding to a *yaml* file."
                        f"The problem occurs at key: {flat_key}"
                    )
                # Remove the tag in the dict
                del flat_config.dict[flat_key]
                flat_config.dict[clean_tag(flat_key, "merge_add")] = val
                # Pre-merge process the dict with the process list of
                # the current config
                flat_config_to_merge = merge_flat_paths_processing(
                    Config({}, []),
                    val,
                    additional_process=flat_config.process_list,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                    postprocess=False,
                )
                clean_dict, _ = dict_clean_tags(flat_config.dict)
                clean_dict_to_merge, _ = dict_clean_tags(flat_config_to_merge.dict)
                for key in clean_dict_to_merge:
                    if clean_all_tags(key) in clean_dict:
                        raise ValueError(
                            f"@merge_add doest not allow to add already "
                            f"existing keys but key '{key}' is found in both "
                            "dicts. Use @merge_after or @merge_before if you "
                            "want to merge this key, or check your key names."
                        )
                # Merge the dicts (order is not important by construction)
                # NOTE: we delete the process list of the current config
                # to speed up the process by avoiding redundant processing
                flat_config = merge_flat_processing(
                    Config(flat_config.dict, []),
                    flat_config_to_merge,
                    allow_new_keys=True,
                    preprocess_first=False,  # Already processed
                    preprocess_second=False,  # Already processed
                    postprocess=False,
                )
        return flat_config


class ProcessCopy(Processing):
    """Copy a value with `@copy` tag. The copy is protected from direct updates.

    Tag your key with `@copy` and with value the name of the flat key to copy.
    The pre-merge processing removes the tag. The post-merge processing
    sets the value (if the copied key exists). The end-build processing checks
    that the key to copy exists and copy them. The pre-save processing
    restores the tag and the key to copy to keep the information on future loads.
    The post-merge and the end-build processings occur after most processings to
    allow the user to modify or add the copied key before the copy.
    Pre-merge order: 0.0
    Post-merge order: 10.0
    End-build order: 10.0
    Pre-save order: 0.0

    Examples
    --------
    ```yaml
    # config.yaml
    a:
        b: 1
        c@copy: a.b
    ```

    Before merging, the config is interpreted as the dict

    ```python
    {'a': {'b': 1, 'c': 1}}
    ```

    Notes
    -----
    * The copy key is protected against any modification and will raise an error
        if you try to modify it but will be updated if the copied key is updated.
    * If the key to copy does not exist in the config on post-merge, no error
        is raised to let the user the possibility to add the key later via merge.
        However, if the key still does not exist at the end of the build
        (and the key was never copied), an error is raised.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 0.0
        self.postmerge_order = 10.0
        self.endbuild_order = 10.0
        self.presave_order = 0.0
        self.keys_to_copy: Dict[str, str] = {}
        self.current_value: Dict[str, Any] = {}

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, val in items:
            if is_tag_in(flat_key, "copy"):
                if not isinstance(val, str):
                    raise ValueError(
                        "Key with '@copy' tag must be associated "
                        "to a string corresponding to a flat key. "
                        f"The problem occurs at key: {flat_key} with value: {val}"
                    )
                clean_key = clean_all_tags(flat_key)
                if (
                    clean_key in self.keys_to_copy
                    and self.keys_to_copy[clean_key] != val
                ):
                    raise ValueError(
                        "Key with '@copy' has change its value to copy. Found key: "
                        f"{flat_key} with value: {val}, previous value to copy: "
                        f"{self.keys_to_copy[clean_key]}"
                    )
                # Store the key to copy and value
                self.keys_to_copy[clean_key] = val
                self.current_value[clean_key] = val
                # Remove the tag and update the dict
                flat_config.dict[clean_tag(flat_key, "copy")] = val
                del flat_config.dict[flat_key]
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        for key, val in self.keys_to_copy.items():
            # NOTE: Do not raise an error if the key to copy does not exist
            # yet because it can be added later in a future merge
            if key in flat_config.dict and val in flat_config.dict:
                if flat_config.dict[key] != self.current_value[key]:
                    # The key has been modified
                    raise ValueError(
                        "Found attempt to modify a key with '@copy' tag. The key "
                        f"is protected against direct updates. Found key: {key} of "
                        f"value {flat_config.dict[key]} that copy {val} of value "
                        f"{flat_config.dict[val]}"
                    )
                # Copy the value
                flat_config.dict[key] = flat_config.dict[val]
                # Update the current value
                self.current_value[key] = flat_config.dict[val]
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing."""
        for key, val in self.keys_to_copy.items():
            if key in flat_config.dict:
                if val in flat_config.dict:
                    # Copy the value
                    flat_config.dict[key] = flat_config.dict[val]
                else:
                    raise ValueError(
                        "A key with '@copy' tag has been found but the key to copy "
                        "does not exist at the end of the build and it has been "
                        f"never copied. Found key: {key} that would copy the "
                        f"key: {val}."
                    )
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        # Restore the tag with the key to copy to keep the information
        # on further loading
        keys = list(flat_config.dict.keys())
        for key in keys:
            clean_key = clean_all_tags(key)
            if clean_key in self.keys_to_copy:
                new_key = key + "@copy"
                del flat_config.dict[key]
                flat_config.dict[new_key] = self.keys_to_copy[clean_key]
        return flat_config


class ProcessDef(Processing):
    """Dynamically define a value from math expression with `@def` tag.

    The expression can contain any parameter name of the configuration.
    The most usefull operators and built-in functions are supported,
    the random and math packages are also supported as well as some (safe)
    numpy, jax, tensorflow, pytorch functions. If/else statements and
    comprehension lists are also supported.

    The pre-merge processing removes the tag. The post-merge processing
    sets the value while the presave processing restore the tag and the
    expression.
    The post-merge processing occurs after most processings to
    allow the user to modify the used keys before the calculation.
    Pre-merge order: 0.0
    Post-merge order: 10.0
    Pre-save order: 0.0

    Examples
    --------
    ```yaml
    # config.yaml
    a:
        b: 1
        c: 2
    d@def: "(a.b + a.c) * 2 > 5"
    ```

    Before merging, the config is interpreted as the dict

    ```python
    {'a': {'b': 1, 'c': 2}, 'd': True}
    ```

    Now the parameter d is automatically updated if a.b or a.c changes
    while also remaining editable by it-self.

    Notes
    -----
    * Unlike @copy processing you can change the value by setting
        an other value or an other definition with @def.
    * Unlike copy processing all the keys used in expression
        must be in the config at post-merge.
    * This processing does not use `eval` and is therefore safe from
        malicious code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 0.0
        self.postmerge_order = 10.0
        self.endbuild_order = 0.0
        self.exprs: Dict[str, str] = {}
        self.values: Dict[str, Any] = {}

    def calc_func(self, expr: str, config: Config) -> Any:
        """Evaluate expression with ast."""
        tree = ast.parse(expr, mode="eval")
        return _process_node(node=tree.body, flat_dict=config.dict)

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, val in items:
            if is_tag_in(flat_key, "def"):
                if not isinstance(val, str):
                    raise ValueError(
                        "Key with '@def' tag must be associated "
                        "to a string corresponding to a math expression to evaluate. "
                        f"The problem occurs at key: {flat_key} with value: {val}"
                    )
                clean_key = clean_all_tags(flat_key)
                # Store the expression
                self.exprs[clean_key] = val
                self.values[clean_key] = val
                # Remove the tag and update the dict
                flat_config.dict[clean_tag(flat_key, "def")] = val
                del flat_config.dict[flat_key]
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        items = list(self.exprs.items())
        for key, expr in items:
            if key in flat_config.dict:
                result = self.calc_func(expr=expr, config=flat_config)
                value = flat_config.dict[key]
                if value != self.values[key]:
                    # The value has changed => remove definition
                    del self.exprs[key]
                else:
                    flat_config.dict[key] = result
                    self.values[key] = result
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        # Restore the tag with the expression to keep the information
        # on further loading
        keys = list(flat_config.dict.keys())
        for key in keys:
            clean_key = clean_all_tags(key)
            if clean_key in self.exprs:
                new_key = key + "@def"
                del flat_config.dict[key]
                flat_config.dict[new_key] = self.exprs[clean_key]
        return flat_config


class ProcessTyping(Processing):
    """Try to convert and force a type with `@type:<mytype>` tag.

    The type is forced forever.
    Allow basic types (none, any, bool, int, float, str, list, dict), nested lists,
    nested dicts, unions (with Union or the '|' symbol) and Optional.
    The type description is lowercased and spaces are removed.

    For instance: `@type:None|List[Dict[str, int|float]]` is valid and force
    the type to be None or a list containing dicts with str keys and int or float
    values.

    The processing stores the type in pre-merge and convert/check alls forced
    types on end-build. It restore the tag in pre-save to keep the information
    on future loads. The end-build processing occurs after almost all processings.
    Pre-merge order: 0.0
    End-build order: 20.0
    Pre-save order: 0.0

    Notes
    -----
    * The conversion into union type is from left to right. For instance,
        `param@type:List[str|float]: [True]` is converted to `["True"]`.
    * The type is not checked on pre-merge or post-merge to allow the parameter
        to be updated (by a copy or a merge for instance). The goal of this
        processing is to ensure the type at the end of the build.


    Examples
    --------
    ```python
    in_dict = {"param@type:None|List[int|float]": None}
    dict1 = {param: [0, 1, 2.0]}  # no error
    dict2 = {param: [0, 1, 2.0, 'a']}  # error
    dict3 = {param: [0, 1, "2"]}  # no error but convert to [0, 1, 2]
    ```

    Merging configs with dictionaries `in_dict` and `dict1` raises no
    error and `param` is forced to be None or a list of int or float forever.
    Merging config with `in_dict` and `dict2` raises an error on post-merge
    due to the 'a' value (which is a string).
    Merging config with `in_dict` and `dict3` raises no error and convert
    the value to [0, 1, 2].

    Note that removing "None|" in the type description of `param` still
    doesn't raise an error in those cases because the type checking is
    evaluated after the merge with `dict2`.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 0.0
        self.endbuild_order = 20.0
        self.presave_order = 0.0
        self.forced_types: Dict[str, tuple] = {}
        self.type_desc: Dict[str, str] = {}  # For error messages

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, val in items:
            end_key = flat_key.split(".")[-1]
            if "@type:" in end_key:
                # Get the type description
                trail = end_key.split("@type:")[-1]
                type_desc = trail.split("@")[0]  # (in case of multiple tags)
                expected_type = tuple(_parse_type(type_desc))
                clean_key = clean_all_tags(flat_key)
                if clean_key in self.forced_types and set(
                    self.forced_types[clean_key]
                ) != set(expected_type):
                    raise ValueError(
                        f"Find the tag '@type:{type_desc}' on a key that has already "
                        "been associated to an other type: "
                        f"{self.type_desc[clean_key]}. "
                        f"Find problem at key: {flat_key}"
                    )
                # Remove the tag
                del flat_config.dict[flat_key]
                flat_config.dict[clean_tag(flat_key, f"type:{type_desc}")] = val
                # Store the forced type
                self.forced_types[clean_key] = expected_type
                self.type_desc[clean_key] = type_desc
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing."""
        for key, expected_type in self.forced_types.items():
            if key in flat_config.dict:
                value = flat_config.dict[key]
                if not _isinstance(value, expected_type):
                    # Trying to convert the value to the expected type
                    value = _convert_type(value, expected_type)
                    if not _isinstance(value, expected_type):
                        type_desc = self.type_desc[key]
                        raise ValueError(
                            f"Key previously tagged with '@type:{type_desc}' must be "
                            f"associated to a value of type {type_desc}. Find the "
                            f"value: {flat_config.dict[key]} of type "
                            f"{type(flat_config.dict[key])} at key: {key}"
                        )
                    flat_config.dict[key] = value
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        # Restore the tag with the type to keep the information
        # on further loading
        keys = list(flat_config.dict.keys())
        for key in keys:
            clean_key = clean_all_tags(key)
            if clean_key in self.type_desc:
                new_key = key + f"@type:{self.type_desc[clean_key]}"
                flat_config.dict[new_key] = flat_config.dict[key]
                del flat_config.dict[key]
        return flat_config


class ProcessSelect(Processing):
    """Select a sub-config with `@select` and delete the rest of its parent config.

    First look in pre-merge for a parameter tagged with `@select` containing a
    flat key corresponding to a sub-configurations to keep. The parent configuration
    is then deleted on post-merge, except the selected sub-configuration
    and eventually the tagged parameter (if it is in the same sub-configuration).
    It is also possible to select multiple keys of a same sub-configuration
    (meaning that the part before the last dot must be equal) by passing a
    list of flat keys.
    Pre-merge order: 0.0
    Post-merge order: 0.0

    Examples
    --------
    ```yaml
    models:
        model_names@select: [models.model1, models.model3]
        model1:
            param1: 1
            param2: 2
        model2:
            param1: 3
            param2: 4
        model3:
            submodel:
                param: 5
        model4:
            param: 6
    ```

    Result in deleting `models.model2` (`param1` and `param2`) and
    `models.model4.param`, and keeping the rest.

    Warns
    -----
    For security reasons, this processing prevents from deleting
    the configuration at the root, which is the case when the
    selected key doesn't contain a dot. It raises an error in this case.
    """

    def __init__(self) -> None:
        super().__init__()
        self.keys_that_select: Set[str] = set()
        self.subconfigs_to_delete: Set[str] = set()
        self.keys_to_keep: Set[str] = set()

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, val in items:
            if is_tag_in(flat_key, "select"):
                # Remove the tag
                clean_key = clean_all_tags(flat_key)
                del flat_config.dict[flat_key]
                flat_config.dict[clean_tag(flat_key, "select")] = val
                self.keys_that_select.add(clean_key)
                if isinstance(val, str):
                    subconfig = ".".join(flat_key.split(".")[:-1])
                    keys_to_keep = [clean_key, val]
                elif isinstance(val, list):
                    subconfig = ".".join(val[0].split(".")[:-1])
                    for key in val[1:]:
                        subconfig2 = ".".join(key.split(".")[:-1])
                        if subconfig != subconfig2:
                            raise ValueError(
                                "The keys in the list of parameters tagged with "
                                "'@select' must be identical before the last dot "
                                f"(= on the same subconfig). Find: {subconfig} and "
                                f"{subconfig2} before the last dot."
                            )
                    keys_to_keep = [clean_key] + val
                else:
                    raise ValueError(
                        "The value of parameters tagged with '@select' must be a "
                        "string or a list of strings representing flat key(s). "
                    )
                subconfig = clean_all_tags(subconfig)
                if subconfig == "":
                    raise ValueError(
                        "Find attempt to delete the configuration at the root. You "
                        "must pass a flat key with a least one dot on parameter "
                        f"tagged with @select. Find key: {flat_key} with value: {val}"
                    )
                self.subconfigs_to_delete.add(subconfig)
                self.keys_to_keep.update(keys_to_keep)
        return flat_config

    def _is_in_subconfig(self, key: str, subconfig: str) -> bool:
        """Check if a key is in a subconfig with the exact name."""
        return key == subconfig or key.startswith(subconfig + ".")

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        # Delete all keys on the subconfigs except the ones to keep
        for subconfig in self.subconfigs_to_delete:
            for key in list(flat_config.dict.keys()):
                if self._is_in_subconfig(key, subconfig) and not any(
                    self._is_in_subconfig(key, key_to_keep)
                    for key_to_keep in self.keys_to_keep
                ):
                    del flat_config.dict[key]
        return super().postmerge(flat_config)

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        # Restore the tag with the type to keep the information
        # on further loading
        keys = list(flat_config.dict.keys())
        for key in keys:
            clean_key = clean_all_tags(key)
            if clean_key in self.keys_that_select:
                new_key = key + "@select"
                flat_config.dict[new_key] = flat_config.dict[key]
                del flat_config.dict[key]
        return flat_config


class ProcessDelete(Processing):
    """Delete the sub-configs/parameters tagged with `@delete` on pre-merge.

    This processing is useful to activate a processing without adding
    an additional parameter in the default configuration to avoid the error
    on merge with `allow_new_keys=False`. This processing is applied very
    late on pre-merge to allow the others processing to be applied before
    deleting the parameters.
    Pre-merge order: 30.0

    Examples
    --------
    ```yaml
    # main.yaml
    1@select@delete: configs.config1
    2@merge_add@delete: config1.yaml
    3@merge_add@delete: config2.yaml

    # config1.yaml
    configs.config1.param: 1
    configs.config1.param2: 2

    # config2.yaml
    configs.config2.param: 3
    configs.config2.param: 4
    ```

    Here we want to merge two config files and select one sub-config.
    We use the corresponding tags but we don't have a good name for the keys
    and instead of adding a new parameter in the default configuration with
    random names like "1", "2", "3", we use the `@delete` tag to delete the
    keys after the pre-merge processing.

    Warns
    -----
    The sub-config/parameter is deleted on pre-merge. Therefore, if the parameter
    also exists on the other configuration during merge (without the tag),
    this parameter will be remain as it is. This processing is more used
    to delete parameter that is NOT present in the default configuration.
    """

    def __init__(self) -> None:
        super().__init__()
        # After all pre-merge processing
        self.premerge_order = 30.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        keys = list(flat_config.dict.keys())
        for key in keys:
            if is_tag_in(key, "delete", full_key=True):
                del flat_config.dict[key]
        return flat_config


class ProcessNew(Processing):
    """Allow new sub-config/parameter absent from default config with tag `@new`.

    The tagged sub-config/parameter and its value is stored during pre-merge and
    is deleted to avoid error on merge due to new key. It is then restored on
    post-merge. Finally, the tag is restored on pre-save for further loading.
    This processing is applied very late on pre-merge to allow
    the others processing to be applied before deleting the parameters.
    The post-merge processing is applied very early to allow the other processing
    to use this new parameter.
    Pre-merge order: 30.0
    Post-merge order: -20.0
    Pre-save order: 0.0

    Disclaimer: It is preferable to have an exhaustive default configuration instead
    of abusing this processing to improve the readability and to avoid typos errors
    in the name of the parameters or their sub-configs.

    Examples
    --------
    ```yaml
    # default.yaml
    param1: 1

    # additional.yaml
    param2@new: 2
    subconfig@new.subsubconfig:
        param3: 3
        param4: 4
    ```

    Use default.yaml as default configuration and add additional.yaml as additional
    configuration via CLI results on the configuration containing param1, param2
    and the nested config containing param3 and param4.
    Without the `@new` tag, an error is raised because param2 is not present in
    the default configuration.

    Notes
    -----
    * Tag a subconfig by adding `@new` at the end of the key containing
        the sub-config dict in your yaml file.
    * When a parameter is added with this processing, it is possible to modify it
        later via config merge without the tag because the parameter is then present
        in the current configuration.
    * If the tagged parameter or sub-config is already present in the current
        configuration, no error are raised and the value is still updated on
        post-merge. It may no have influence in practice.
    """

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = 30.0
        self.postmerge_order = -20.0
        self.new_vals: Dict[str, Any] = {}
        self.new_vals_backup: Dict[str, Any] = {}

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        keys = list(flat_config.dict.keys())
        for key in keys:
            # NOTE: we don't use is_tag_in because we want to look
            # for tags in the sub-configs too.
            if "@new@" in key or "@new." in key or key.endswith("@new"):
                clean_key = clean_all_tags(key)
                self.new_vals[clean_key] = flat_config.dict[key]
                self.new_vals_backup[clean_key] = flat_config.dict[key]
                del flat_config.dict[key]
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        flat_config.dict.update(self.new_vals)
        # Reset the new values to avoid re-adding them later
        self.new_vals = {}
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        # Restore the tag @new to allow loading the config later by allowing
        # these new parameters.
        for key, value in self.new_vals_backup.items():
            if key in flat_config.dict:
                flat_config.dict[key + "@new"] = value
                del flat_config.dict[key]
        return flat_config


class ProcessDict(Processing):
    """Declare a dict instead of a sub-config with `@dict` tag.

    This processing  can be used to declare a dict where the keys
    are not known in advance or will be modified. New keys are allowed
    in each merge and the element are still available using the dot
    notation like `config.subconfig.mydict.something`.
    The pre-merge processing removes the tag and converts the dict to
    a wrapped dict to prevent the flattening. The end-build processing
    unwraps the dicts to a normal dict. The pre-save processing restores
    the tag to keep the information on future loads.
    Pre-merge order: -30.0
    End-build order: 0.0
    Pre-save order: -30.0

    Examples
    --------
    ```yaml
    # default.yaml
    param1: 0
    param2: 2
    sweep@dict: None

    # additional1.yaml
    sweep@dict:
        metric: {name: accuracy, goal: maximize}
        method: bayes
        parameters:
        param1: {min: 0, max: 50}

    # additional2.yaml
    sweep@dict:
        name: "random sweep"
        method: random
        parameters:
        param2: {min: 0, max: 10}
    ```

    The `swep` parameter is considered as a single dict object
    and not as a sub-config for merging.

    Warns
    -----
    * Processings are not applied in the dict keys. In particular,
        the tags are not used and not removed.
    * The tag `@dict` must be added at the key containing
        the dict every time you want to modify the dict.
    """

    class PseudoDict:
        """Object containing a dict that dodges flattening."""

        def __init__(self, dict_: dict):
            self.dict = dict_

        def __repr__(self) -> str:
            """Representation."""
            return f"PseudoDict({self.dict})"

        def __str__(self) -> str:
            """Representation as string."""
            return f"PseudoDict({self.dict})"

    def __init__(self) -> None:
        super().__init__()
        self.premerge_order = -30.0
        self.endbuild_order = 0.0
        self.presave_order = -30.0
        self.keys_with_dict: Set[str] = set()

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        keys = list(flat_config.dict.keys())
        splitter: TypeSplitDict = {}
        for key in keys:
            if is_tag_in(key, "dict", full_key=True):
                splitter = self._split_dict_key(splitter, key, flat_config.dict[key])
                del flat_config.dict[key]
        new_dict = {}
        for key, values in splitter.items():
            new_dict[key] = self.PseudoDict(unflatten(dict(values)))
            self.keys_with_dict.add(clean_all_tags(key))
        flat_config.dict.update(new_dict)
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing."""
        for key in flat_config.dict:
            if isinstance(flat_config.dict[key], self.PseudoDict):
                flat_config.dict[key] = flat_config.dict[key].dict
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        keys = list(flat_config.dict.keys())
        for key in keys:
            if key.startswith(tuple(self.keys_with_dict)):
                for key_dict in self.keys_with_dict:
                    # Add the tag @dict to the key to keep the information
                    if key.startswith(key_dict):
                        new_key = key_dict + "@dict" + key[len(key_dict) :]
                        flat_config.dict[new_key] = flat_config.dict[key]
                        del flat_config.dict[key]
                        break
        return flat_config

    def _split_dict_key(
        self,
        splitter: TypeSplitDict,
        flat_key: str,
        value: Any,
    ) -> TypeSplitDict:
        """Split a key by @dict."""
        split_dict = flat_key.split("@dict")
        # Handle the case where there is another @dict in the key
        split_dict = [split_dict[0]] + ["@dict".join(split_dict[1:])]
        # Include the other tags in the key
        split_dot = split_dict[1].split(".")
        split_dot = [split_dot[0]] + [".".join(split_dot[1:])]

        main_key = split_dict[0] + split_dot[0]
        dict_key = split_dot[1]
        if main_key not in splitter:
            splitter[main_key] = [(dict_key, value)]
        else:
            splitter[main_key].append((dict_key, value))
        return splitter


class ProcessCheckTags(Processing):
    """Raise an error if a tag is present in a key after pre-merging processes.

    This security processing is always applied after all pre-merge process and
    checks for '@' in the keys. It raises an error if one is found.
    """

    def __init__(self) -> None:
        super().__init__()
        # NOTE: this processing is a special meta-processing that must be
        # applied after all other pre-merge processing to ensure security.
        # That why it has a very high pre-merge order and it is not a
        # good idea to make pre-merge processing with higher order.
        self.premerge_order = 1000.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        _, tagged_keys = dict_clean_tags(flat_config.dict)
        if tagged_keys:
            keys_message = "\n".join(tagged_keys[:5])
            raise ValueError(
                "Keys with tags are encountered at the end of "
                "the pre-merge process. It is probably a mistake due to:\n"
                "- a typo in tag name\n"
                "- a missing processing in process_list\n"
                "- the use of an 'at' ('@') in a parameter name\n"
                "- the use of a custom processing that does not remove a tag\n\n"
                "The tagged keys encountered (5 first if more than 5) are:\n"
                f"{keys_message}"
            )
        return flat_config


class DefaultProcessings:
    """Default list of built-in processings.

    To add these processings to a Config instance, use:
    ```python
    config.process_list += DefaultProcessings().list
    ```

    The current default processing list contains:
     * ProcessCheckTags: protect against '@' in keys at the end of pre-merge)
     * ProcessMerge (@merge_all, @merge_before, @merge_after): merge multiple
       files into one.
     * ProcessCopy (@copy): persistently copy a value from one key to an other
       and protect it
     * ProcessTyping (@type:X): force the type of parameter to any type X.
     * ProcessSelect (@select): select sub-config(s) to keep and delete the
       other sub-configs in the same parent config.
     * ProcessDelete (@delete): delete the parameter tagged with @delete on
       pre-merge.
    """

    def __init__(self) -> None:
        self.list: List[Processing] = [
            ProcessCheckTags(),
            ProcessMerge(),
            ProcessCopy(),
            ProcessDef(),
            ProcessTyping(),
            ProcessSelect(),
            ProcessDelete(),
            ProcessDict(),
            ProcessNew(),
        ]
