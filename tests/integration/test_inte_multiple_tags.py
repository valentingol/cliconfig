"""Integration test for multiple tags."""
import sys

import pytest
import pytest_check as check

from cliconfig import make_config
from cliconfig.base import Config
from cliconfig.process_routines import merge_flat_processing


def test_multiple_tags() -> None:
    """Integration test for multiple tags."""
    sys_argv = sys.argv.copy()
    sys.argv = ["test_inte_multiple_tags.py"]
    config = make_config("tests/configs/integration/main.yaml")
    expected_config = {
        "path_1": "tests/configs/integration/sub1.yaml",
        "path_2": "tests/configs/integration/sub2.yaml",
        "config1": {
            "param": 2,
            "param2": 1,
        },
        "config2": {
            "param": 2,
        },
    }
    check.equal(config.dict, expected_config)
    with pytest.raises(
        ValueError,
        match="Key previously tagged with '@type:None|int'.*"
    ):
        merge_flat_processing(
            config,
            Config({'config2.param': 5.6}, []),
            preprocess_first=False,
        )
    sys.argv = sys_argv
