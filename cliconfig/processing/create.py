"""Functions to create new processing quickly."""
# pylint: disable=unused-argument
import re
from typing import Callable, Optional, Set

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
        func: Callable,
    ) -> None:
        super().__init__()
        self.premerge_order = order
        self.regex = regex
        self.tag_name = tag_name
        self.func = func
        if self.regex:
            self.is_in_func = lambda key: re.match(self.regex, key.split('.')[-1])
        else:
            self.is_in_func = lambda key: is_tag_in(key, self.tag_name)

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
        func: Callable,
    ) -> None:
        super().__init__()
        self.premerge_order = order
        self.regex = regex
        self.tag_name = tag_name
        self.func = func
        self.matched_keys: Set[str] = set()
        if self.regex:
            self.is_in_func = lambda key: re.match(self.regex, key.split('.')[-1])
        else:
            self.is_in_func = lambda key: is_tag_in(key, self.tag_name)

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if (self.is_in_func(flat_key)  # type: ignore
                    or clean_all_tags(flat_key) in self.matched_keys):
                self.matched_keys.add(clean_all_tags(flat_key))
                if self.tag_name:
                    del flat_config.dict[flat_key]
                    flat_key = clean_tag(flat_key, self.tag_name)
                flat_config.dict[flat_key] = self.func(value)
        return flat_config


def create_processing_value(
    func: Callable,
    regex: Optional[str] = None,
    tag_name: Optional[str] = None,
    order: float = 0.0,
    *,
    persistent: bool = False,
) -> Processing:
    r"""Create a processing object that modifies a value in dict using tag or regex.

    The processing is applied on premerge. It triggers when the key matches
    the tag or the regex. The function apply flat_dict[key] = func(flat_dict[key]).
    You must only provide one of tag or regex. If tag is provided, the tag will be
    removed from the key during premerge.

    Parameters
    ----------
    func : Callable
        The function to apply to the value to make new_value.
    regex : Optional[str]
        The regex to match the key.
    tag_name : Optional[str]
        The tag (without "@") to match the key. The values are modified when
        triggering the pattern ".*@<tag_name>.*" and the tag is removed from the key.
    order : int, optional
        The premerge order. By default 0.0.
    persistent : bool, optional
        If True, the processing will be applied on all keys that have already
        matched the tag before. By nature, regex processing are always persistent.
        By default, False.

    Raises
    ------
    ValueError
        If both tag and regex are provided or if none of them are provided.

    Returns
    -------
    processing : Processing
        The processing object with the premerge method.


    Examples
    --------
    With the following 2 processing and the following config:

    ::

        proc2 = create_processing_value(lambda x: -x, regex="neg_number.*", order=0.0)
        proc1 = create_processing_value(lambda x: x + 1, tag_name="add1", order=1.0)

    .. code_block: yaml

        --- # config.yaml
        neg_number1: 1
        neg_number2: 1
        neg_number3@add1: 1

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
            raise ValueError("You must provide a tag or a regex "
                             "(to trigger the value update).")
    if persistent:
        return _ProcessingValuePersistent(regex, tag_name, order, func)
    return _ProcessingValue(regex, tag_name, order, func)
