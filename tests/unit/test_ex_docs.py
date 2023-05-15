"""Test ProcessBypassTyping."""

from typing import Dict, Set

import pytest
import pytest_check as check

from cliconfig import Config
from cliconfig.process_routines import merge_flat_processing
from cliconfig.processing.base import Processing
from cliconfig.processing.builtin import ProcessTyping
from cliconfig.tag_routines import clean_all_tags, clean_tag, is_tag_in


class ProcessPrintSorted(Processing):
    """Print the parameters tagged with "@look", sorted by value on post-merge."""

    def __init__(self) -> None:
        super().__init__()
        self.looked_keys: Set[str] = set()
        # Pre-merge just look for the tag so order is not important
        self.premerge_order = 0.0
        # Post-merge should be after the copy processing if we want the final values
        # on post-merge
        self.postmerge_order = 15.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        # Browse a freeze version of the dict (because we will modify it to remove tags)
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "look"):  # Check if the key contains the tag
                # Remove the tag and update the dict
                new_key = clean_tag(flat_key, "look")
                flat_config.dict[new_key] = value
                del flat_config.dict[flat_key]
                # Store the key
                # remove all tags = true parameter name
                clean_key = clean_all_tags(flat_key)
                self.looked_keys.add(clean_key)
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        values = []
        for key in self.looked_keys:
            # IMPORTANT
            # ("if key in flat_config.dict:" is important in case of some keys were
            # removed or if multiple dicts with different parameters are seen by
            # the processing)
            if key in flat_config.dict:
                values.append(flat_config.dict[key])
        print("The sorted looked values are: ", sorted(values))
        # If we don't want to keep the looked keys for further print:
        self.looked_keys = set()

        return flat_config


class ProcessBypassTyping(Processing):
    """Bypass type check of ProcessTyping for parameters tagged with "@bypass_typing".

    In pre-merge it looks for a parameter with the tag "@bypass_typing",
    removes it and change the internal ProcessTyping variables to avoid
    checking the type of the parameter with ProcessTyping.
    """

    def __init__(self) -> None:
        super().__init__()
        self.bypassed_forced_types: Dict[str, tuple] = {}
        # Before ProcessTyping pre-merge to let it change the type
        self.premerge_order = -1.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "bypass_typing"):
                new_key = clean_tag(flat_key, "bypass_typing")
                flat_config.dict[new_key] = value
                del flat_config.dict[flat_key]
                clean_key = clean_all_tags(flat_key)
                for processing in flat_config.process_list:
                    if (
                        isinstance(processing, ProcessTyping)
                        and clean_key in processing.forced_types
                    ):
                        forced_type = processing.forced_types.pop(clean_key)
                        self.bypassed_forced_types[clean_key] = forced_type
        return flat_config


def test_process_print_sorted(capsys: pytest.CaptureFixture) -> None:
    """Test ProcessPrintSorted."""
    config1 = Config({"a@look": 0, "b@look": 2, "c": 3}, [ProcessPrintSorted()])
    config2 = Config({"a@look": 1, "d@look": 4}, [])
    capsys.readouterr()
    merge_flat_processing(config1, config2)
    out = capsys.readouterr().out
    check.equal(out, "The sorted looked values are:  [1, 2, 4]\n")


def test_process_bypass_typing() -> None:
    """Test ProcessBypassTyping."""
    config1 = Config({"a@type:int": 0}, [ProcessBypassTyping(), ProcessTyping()])
    config2 = Config({"a@bypass_typing@type:str": "a"}, [])
    merge_flat_processing(config1, config2)
    config1 = Config({"a@type:int": 0}, [ProcessBypassTyping(), ProcessTyping()])
    config2 = Config({"a@type:str": "a"}, [])
    # Reset ProcessTyping
    with pytest.raises(
        ValueError,
        match=(
            "Find the tag '@type:str' on a key that has already "
            "been associated to an other type: int.*"
        ),
    ):
        merge_flat_processing(config1, config2)
