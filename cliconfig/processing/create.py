"""Functions to create new processing quickly."""
# pylint: disable=unused-argument
import re
from typing import Any, Callable, Dict, Optional, Set

from cliconfig.base import Config
from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_all_tags, clean_tag, is_tag_in


class _ProcessingValue(Processing):
    """Processing class for make_processing_value."""

    def __init__(
        self,
        regex: Optional[str],
        tag_name: Optional[str],
        order: float,
        func: Callable[[Any], Any],
    ) -> None:
        super().__init__()
        self.premerge_order = order
        self.regex = regex
        self.tag_name = tag_name
        self.func = func
        if self.regex:
            self.is_in_func = (
                lambda key: re.match(self.regex, key.split(".")[-1]) is not None
            )
        elif self.tag_name:
            self.is_in_func = lambda key: is_tag_in(key, str(self.tag_name))

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if self.is_in_func(flat_key):  # type: ignore
                if self.tag_name:
                    del flat_config.dict[flat_key]
                    flat_key = clean_tag(flat_key, self.tag_name)
                flat_config.dict[flat_key] = self.func(value)
        return flat_config


class _ProcessingValuePersistent(Processing):
    """Processing class for make_processing_value. Persistent version."""

    def __init__(
        self,
        regex: Optional[str],
        tag_name: Optional[str],
        order: float,
        func: Callable[[Any], Any],
    ) -> None:
        super().__init__()
        self.premerge_order = order
        self.regex = regex
        self.tag_name = tag_name
        self.func = func
        self.matched_keys: Set[str] = set()
        if self.regex is not None:
            self.is_in_func = (
                lambda key: re.match(self.regex, key.split(".")[-1]) is not None
            )
        elif self.tag_name is not None:
            self.is_in_func = lambda key: is_tag_in(key, str(self.tag_name))

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if (
                self.is_in_func(flat_key)  # type: ignore
                or clean_all_tags(flat_key) in self.matched_keys
            ):
                self.matched_keys.add(clean_all_tags(flat_key))
                if self.tag_name:
                    del flat_config.dict[flat_key]
                    flat_key = clean_tag(flat_key, self.tag_name)
                flat_config.dict[flat_key] = self.func(value)
        return flat_config


class _ProcessingKeepProperty(Processing):
    """Processing class for make_processing_keep_property."""

    def __init__(
        self,
        regex: Optional[str],
        tag_name: Optional[str],
        premerge_order: float,
        postmerge_order: float,
        func: Callable,
    ) -> None:
        super().__init__()
        self.premerge_order = premerge_order
        self.postmerge_order = postmerge_order
        self.regex = regex
        self.tag_name = tag_name
        self.func = func
        self.properties: Dict[str, Any] = {}
        if self.regex is not None:
            self.is_in_func = (
                lambda key: re.match(self.regex, key.split(".")[-1]) is not None
            )
        elif self.tag_name is not None:
            self.is_in_func = lambda key: is_tag_in(key, str(self.tag_name))

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if self.is_in_func(flat_key):  # type: ignore
                property_ = self.func(value)
                clean_key = clean_all_tags(flat_key)
                if clean_key not in self.properties:
                    self.properties[clean_key] = property_
                if self.tag_name:
                    del flat_config.dict[flat_key]
                    flat_key = clean_tag(flat_key, self.tag_name)
                    flat_config.dict[flat_key] = value
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        for flat_key, value in self.properties.items():
            if flat_key in flat_config.dict:
                property_ = self.func(flat_config.dict[flat_key])
                if property_ != value:
                    raise ValueError(
                        f"Property of key {flat_key} has changed from {value} to "
                        f"{property_} while it is protected by a keep-property "
                        "processing (problem found on post-merge)."
                    )
        return flat_config


def create_processing_value(
    func: Callable,
    regex: Optional[str] = None,
    tag_name: Optional[str] = None,
    order: float = 0.0,
    *,
    persistent: bool = True,
) -> Processing:
    r"""Create a processing object that modifies a value in dict using tag or regex.

    The processing is applied on pre-merge. It triggers when the key matches
    the tag or the regex. The function apply ``flat_dict[key] = func(flat_dict[key])``.
    You must only provide one of tag or regex. If tag is provided, the tag will be
    removed from the key during pre-merge.

    Parameters
    ----------
    func : Callable
        The function to apply to the value to make new_value.
    regex : Optional[str]
        The regex to match the key.
    tag_name : Optional[str]
        The tag (without "@") to match the key. The tag is removed from
        the key after triggering.
    order : int, optional
        The pre-merge order. By default 0.0.
    persistent : bool, optional
        If True, the processing will be applied on all keys that have already
        matched the tag before. By nature, regex processing are always persistent.
        By default, True.

    Raises
    ------
    ValueError
        If both tag and regex are provided or if none of them are provided.

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

        proc2 = create_processing_value(lambda x: -x, regex="neg_number.*", order=0.0)
        proc1 = create_processing_value(lambda x: x + 1, tag_name="add1", order=1.0)

    When config.yaml is merged with an other config, it will be considered
    before merging as:

    ::

        {'number1': -1, 'number2': -1, 'number3': 0}
    """
    if tag_name is not None:
        if regex is not None:
            raise ValueError("You must provide a tag or a regex but not both.")
    else:
        if regex is None:
            raise ValueError(
                "You must provide a tag or a regex (to trigger the value update)."
            )
    if persistent:
        return _ProcessingValuePersistent(regex, tag_name, order, func)
    return _ProcessingValue(regex, tag_name, order, func)


def create_processing_keep_property(
    func: Callable,
    regex: Optional[str] = None,
    tag_name: Optional[str] = None,
    premerge_order: float = 0.0,
    postmerge_order: float = 0.0,
) -> Processing:
    """Create a processing object that keep a property from a value using tag or regex.

    The pre-merge processing looks for keys that match the tag or the regex, apply
    the function func on the value and store the result (= the "property"):
    ``property = func(flat_dict[key])``.
    The post-merge processing will check that the property is the same as the one
    stored during pre-merge. If not, it will raise a ValueError.

    Parameters
    ----------
    func : Callable
        The function to apply to the value to define the property to keep.
    regex : Optional[str]
        The regex to match the key.
    tag_name : Optional[str]
        The tag (without "@") to match the key. The values are modified when
        triggering the pattern ".*@<tag_name>.*" and the tag is removed from the key.
    premerge_order : float, optional
        The pre-merge order, by default 0.0
    postmerge_order : float, optional
        The post-merge order, by default 0.0

    Raises
    ------
    ValueError
        If both tag and regex are provided or if none of them are provided.

    Returns
    -------
    Processing
        The processing object with the pre-merge and post-merge methods.

    Note
    ----

        The property to keep can be updated by using the tag a second time.

    Examples
    --------
    A processing that enforce the types of all the parameters to be constant
    (equal to the type of the first value encountered):

    ::

        create_processing_keep_property(type, regex=".*", premerge_order=15.0,
                                        postmerge_order=15.0)

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
        regex, tag_name, premerge_order, postmerge_order, func
    )
    return processing
