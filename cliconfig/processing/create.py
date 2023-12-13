"""Functions to create new processing quickly."""
# pylint: disable=unused-argument
import re
from inspect import signature
from typing import Any, Callable, Dict, Optional, Set, Union

from cliconfig.base import Config
from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_all_tags, clean_tag, is_tag_in


def _is_matched(key: str, tag_name: Optional[str], regex: Optional[str]) -> bool:
    """Check if key match the regex or contain the tag."""
    if tag_name is not None and regex is not None:
        raise ValueError("Either regex or tag_name must be defined but not both.")
    # Case defined with tag
    if tag_name is not None:
        return is_tag_in(key, tag_name)
    # Case defined with regex
    if regex is not None:
        param_name = key.split(".")[-1].split("@")[0]
        return re.match(regex, param_name) is not None
    raise ValueError("Either regex or tag_name must be defined.")


class _ProcessingValue(Processing):
    """Processing class for make_processing_value."""

    def __init__(
        self,
        func: Union[Callable[[Any], Any], Callable[[Any, Config], Any]],
        processing_type: str,
        *,
        regex: Optional[str],
        tag_name: Optional[str],
        order: float,
        persistent: bool,
    ) -> None:
        super().__init__()
        self.func = func
        self.processing_type = processing_type
        self.regex = regex
        self.tag_name = tag_name
        self.order = order
        if processing_type == "premerge":
            self.premerge_order = order
        elif processing_type == "postmerge":
            self.postmerge_order = order
        elif processing_type == "endbuild":
            self.endbuild_order = order
        elif processing_type == "presave":
            self.presave_order = order
        elif processing_type == "postload":
            self.postload_order = order
        else:
            raise ValueError(
                f"Processing type '{processing_type}' not recognized. Must be"
                "one of 'premerge', 'postmerge', 'endbuild', 'presave' or"
                "'postload'."
            )
        self.persistent = persistent
        # matched_keys: store keys that match the regex or contain the tag
        self.matched_keys: Set[str] = set()

    def _apply_update(self, flat_config: Config) -> Config:
        """Apply value updates to matching parameters.

        Does not assume that the keys are clean (it is not always the case
        on pre-merge and post-load for instance).
        """
        items = list(flat_config.dict.items())
        for key, value in items:
            clean_key = clean_all_tags(key)
            if clean_key in self.matched_keys:
                # Remove clean_key from match_keys if not persistent
                if not self.persistent:
                    self.matched_keys.remove(clean_key)

                # Apply update

                value = flat_config.dict[key]
                try:
                    # Case one argument
                    if len(signature(self.func).parameters) == 1:
                        flat_config.dict[key] = self.func(value)  # type: ignore
                    # Case two arguments
                    else:
                        flat_config.dict[key] = self.func(  # type: ignore
                            value, flat_config
                        )
                except ValueError:
                    # Case no signature, trying to call with one argument
                    flat_config.dict[key] = self.func(value)  # type: ignore
        return flat_config

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if _is_matched(flat_key, self.tag_name, self.regex):
                # Store the key
                self.matched_keys.add(clean_all_tags(flat_key))
                # Remove the tag if any
                if self.tag_name:
                    del flat_config.dict[flat_key]
                    new_key = clean_tag(flat_key, self.tag_name)
                    flat_config.dict[new_key] = value

        if self.processing_type == "premerge":
            return self._apply_update(flat_config)
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        if self.processing_type == "postmerge":
            return self._apply_update(flat_config)
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing."""
        if self.processing_type == "endbuild":
            return self._apply_update(flat_config)
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing."""
        if self.processing_type == "presave":
            return self._apply_update(flat_config)
        return flat_config

    def postload(self, flat_config: Config) -> Config:
        """Post-load processing."""
        if self.processing_type == "postload":
            return self._apply_update(flat_config)
        return flat_config

    def __repr__(self) -> str:
        """Representation of Processing object."""
        return (
            f"ProcessingValue(func={self.func.__name__}, tag={self.tag_name}, "
            f"regex={self.regex}, type={self.processing_type}, "
            f"persistent={self.persistent}, order={self.order})"
        )


class _ProcessingKeepProperty(Processing):
    """Processing class for make_processing_keep_property."""

    def __init__(
        self,
        func: Union[Callable[[Any], Any], Callable[[Any, Config], Any]],
        *,
        regex: Optional[str],
        tag_name: Optional[str],
        premerge_order: float,
        postmerge_order: float,
        endbuild_order: float,
    ) -> None:
        super().__init__()
        self.func = func
        self.regex = regex
        self.tag_name = tag_name
        self.premerge_order = premerge_order
        self.postmerge_order = postmerge_order
        self.endbuild_order = endbuild_order

        self.properties: Dict[str, Any] = {}

    def _eval_property(self, key: str, flat_config: Config) -> Any:
        """Evaluate property."""
        try:
            # Case one argument
            if len(signature(self.func).parameters) == 1:
                return self.func(flat_config.dict[key])  # type: ignore
            # Case two arguments
            return self.func(flat_config.dict[key], flat_config)  # type: ignore
        except ValueError:
            # Case no signature, trying to call with one argument
            return self.func(flat_config.dict[key])  # type: ignore

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if _is_matched(flat_key, self.tag_name, self.regex):
                clean_key = clean_all_tags(flat_key)
                if clean_key not in self.properties:
                    property_ = self._eval_property(flat_key, flat_config)
                    self.properties[clean_key] = property_
                if self.tag_name:
                    del flat_config.dict[flat_key]
                    new_key = clean_tag(flat_key, self.tag_name)
                    flat_config.dict[new_key] = value
        return flat_config

    def _check_properties(self, flat_config: Config, processing_timing: str) -> None:
        """Check if all properties are still the same."""
        for flat_key, expected_property in self.properties.items():
            if flat_key in flat_config.dict:
                property_ = self._eval_property(flat_key, flat_config)
                if property_ != expected_property:
                    raise ValueError(
                        f"Property of key {flat_key} has changed from "
                        f"{expected_property} to "
                        f"{property_} while it is protected by a keep-property "
                        f"processing (problem found on {processing_timing})."
                    )

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        self._check_properties(flat_config, "post-merge")
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing."""
        self._check_properties(flat_config, "end-build")
        return flat_config

    def __repr__(self) -> str:
        """Representation of Processing object."""
        return (
            f"ProcessingKeepProperty(func={self.func.__name__}, tag={self.tag_name}, "
            f"regex={self.regex}, orders=({self.premerge_order}, "
            f"{self.postmerge_order}, {self.endbuild_order}))"
        )


def create_processing_value(
    func: Union[Callable[[Any], Any], Callable[[Any, Config], Any]],
    processing_type: str = "premerge",
    *,
    regex: Optional[str] = None,
    tag_name: Optional[str] = None,
    order: float = 0.0,
    persistent: bool = False,
) -> Processing:
    r"""Create a processing object that modifies a value in config using tag or regex.

    The processing is applied on pre-merge. It triggers when the key matches
    the tag or the regex. The function apply ``flat_dict[key] = func(flat_dict[key])``.
    You must only provide one of tag or regex. If tag is provided, the tag will be
    removed from the key during pre-merge.

    It also possible to pass the flat config as a second argument of the function
    ``func``. In this case, the function apply
    ``flat_dict[key] = func(flat_dict[key], flat_config)``.

    Parameters
    ----------
    func : Callable
        The function to apply to the value (and eventually the flat config)
        to make the new value so that:
        flat_dict[key] = func(flat_dict[key]) or func(flat_dict[key], flat_config)
    processing_type : str, optional
        One of "premerge", "postmerge", "presave", "postload" or "endbuild".
        Timing to apply the value update. In all cases the tag is removed on pre-merge.
        By default "premerge".
    regex : Optional[str]
        The regex to match the key.
    tag_name : Optional[str]
        The tag (without "@") to match the key. The tag is removed on pre-merge.
    order : int, optional
        The pre-merge order. By default 0.0.
    persistent : bool, optional
        If True, the processing will be applied on all keys that have already
        matched the tag before. By nature, using regex make the processing
        always persistent. By default, False.

    Raises
    ------
    ValueError
        If both tag and regex are provided or if none of them are provided.
    ValueError
        If the processing type is not one of "premerge", "postmerge", "presave",
        "postload" or "endbuild".

    Returns
    -------
    processing : Processing
        The processing object with the pre-merge method.


    Examples
    --------
    With the following config and 2 processings:

    .. code_block: yaml

        # config.yaml
        neg_number1: 1
        neg_number2: 1
        neg_number3@add1: 1

    ::

        proc2 = create_processing_value(lambda val: -val, regex="neg_number.*",
            order=0.0)
        proc1 = create_processing_value(lambda val: val + 1, tag_name="add1",
            order=1.0)

    When config.yaml is merged with an other config, it will be considered
    before merging as:

    ::

        {'number1': -1, 'number2': -1, 'number3': 0}

    Using the config as a second argument of the function:

    .. code_block: yaml

        # config.yaml
        param1: 1
        param2@eval: "config.param1 + 1"

    ::

        proc = create_processing_value(
            lambda val, config: eval(val, {'config': config}),
            processing_type='postmerge', tag_name='eval', persistent=False
        )

    After config.yaml is merged with another config, param2 will be evaluated
    as 2 (except if config.param1 has changed with a processing before).
    """
    if tag_name is not None:
        if regex is not None:
            raise ValueError("You must provide a tag or a regex but not both.")
    else:
        if regex is None:
            raise ValueError(
                "You must provide a tag or a regex (to trigger the value update)."
            )
    proc = _ProcessingValue(
        func,
        processing_type,
        regex=regex,
        tag_name=tag_name,
        order=order,
        persistent=persistent,
    )
    return proc


def create_processing_keep_property(
    func: Callable,
    regex: Optional[str] = None,
    tag_name: Optional[str] = None,
    premerge_order: float = 0.0,
    postmerge_order: float = 0.0,
    endbuild_order: float = 0.0,
) -> Processing:
    """Create a processing object that keep a property from a value using tag or regex.

    The pre-merge processing looks for keys that match the tag or the regex, apply
    the function func on the value and store the result (= the "property"):
    ``property = func(flat_dict[key])``.
    The post-merge processing will check that the property is the same as the one
    stored during pre-merge. If not, it will raise a ValueError.

    It also possible to pass the flat config as a second argument of the function
    ``func``. In this case, the function apply
    ``property = func(flat_dict[key], flat_config)``.

    Parameters
    ----------
    func : Callable
        The function to apply to the value (and eventually the flat config)
        to define the property to keep.
        property = func(flat_dict[key]) or func(flat_dict[key], flat_config)
    regex : Optional[str]
        The regex to match the key.
    tag_name : Optional[str]
        The tag (without "@") to match the key. The values are modified when
        triggering the pattern ".*@<tag_name>.*" and the tag is removed from the key.
    premerge_order : float, optional
        The pre-merge order, by default 0.0
    postmerge_order : float, optional
        The post-merge order, by default 0.0
    endbuild_order : float, optional
        The end-build order, by default 0.0

    Raises
    ------
    ValueError
        If both tag and regex are provided or if none of them are provided.

    Returns
    -------
    Processing
        The processing object with the pre-merge and post-merge methods.

    Examples
    --------
    A processing that enforce the types of all the parameters to be constant
    (equal to the type of the first value encountered):

    ::

        create_processing_keep_property(type, regex=".*", premerge_order=15.0,
                                        postmerge_order=15.0, endbuild_order=15.0)

    A processing that protect parameters tagged with @protect from being changed:

    ::

        create_processing_keep_property(lambda x: x, tag_name="protect",
                                        premerge_order=15.0, postmerge_order=15.0)
    """
    if tag_name is not None:
        if regex is not None:
            raise ValueError("You must provide a tag or a regex but not both.")
    else:
        if regex is None:
            raise ValueError(
                "You must provide a tag or a regex (to trigger the value update)."
            )
    processing = _ProcessingKeepProperty(
        func,
        regex=regex,
        tag_name=tag_name,
        premerge_order=premerge_order,
        postmerge_order=postmerge_order,
        endbuild_order=endbuild_order,
    )
    return processing
