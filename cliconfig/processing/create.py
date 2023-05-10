"""Functions to create new processing quickly."""
# pylint: disable=unused-argument
import re
from typing import Any, Callable, Dict, List, Optional

from cliconfig.processing.base import Processing
from cliconfig.tag_routines import clean_tag


def create_processing_value(
    func: Callable,
    regex: Optional[str] = None,
    tag_name: Optional[str] = None,
    order: float = 0.0
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
    regex : str
        The regex to match the key.
    tag_name : str
        The tag (without "@") to match the key. The values are modified when
        triggering the pattern ".*@<tag_name>.*" and the tag is removed from the key.
    order : int, optional
        The premerge order. By default 0.0.

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

    .. code_block: python
        proc2 = create_processing_value(lambda x: -x, regex="neg_number.*", order=0.0)
        proc1 = create_processing_value(lambda x: x + 1, tag_name="add1", order=1.0)

    -- code_block: yaml

        --- # config.yaml
        neg_number1: 1
        neg_number2: 1
        neg_number3@add1: 1

    When config.yaml is merged with an other config, it will be considered
    before merging as:

    .. code_block: python
        {'number1': -1, 'number2': -1, 'number3': 0}
    """
    class NewProcessing(Processing):
        """New processing class for make_processing_value."""

        def __init__(self, regex: str, tag_name: Optional[str], order: float) -> None:
            super().__init__()
            self.premerge_order = order
            self.regex = regex
            self.tag_name = tag_name

        def premerge(
            self,
            flat_dict: Dict[str, Any],
            processing_list: List[Processing],  # noqa: ARG002
        ) -> Dict[str, Any]:
            items = list(flat_dict.items())
            for flat_key, value in items:
                end_key = flat_key.split('.')[-1]
                if re.match(self.regex, end_key):
                    if self.tag_name:
                        del flat_dict[flat_key]
                        flat_key = clean_tag(flat_key, self.tag_name)
                    flat_dict[flat_key] = func(value)
            return flat_dict

    if tag_name is not None:
        if regex is not None:
            raise ValueError("You must provide a tag or a regex but not both.")
        return NewProcessing(f'.*@{tag_name}.*', tag_name, order)
    if regex is not None:
        return NewProcessing(regex, tag_name, order)
    raise ValueError("You must provide a tag or a regex (to trigger the value update).")


if __name__ == '__main__':
    print(re.match('.*@add1.*', 'neg_number3@add1'))
