"""Test base class of processing."""

import pytest_check as check

from cliconfig.base import Config
from cliconfig.processing.base import Processing


def test_processing() -> None:
    """Test Processing."""

    class _ProcessingTest(Processing):
        def __init__(self) -> None:
            super().__init__()
            self.attr = 0

    config = Config({"a.b": 1, "b": 2, "c.d.e": 3, "c.d.f": [2, 3]}, [])
    base_process = Processing()
    check.equal(
        (
            base_process.premerge(config),
            base_process.postmerge(config),
            base_process.endbuild(config),
            base_process.presave(config),
            base_process.postload(config),
        ),
        (config, config, config, config, config),
    )
    # Check equality of Processing objects
    proc1 = _ProcessingTest()
    proc1.attr = 0
    proc2 = _ProcessingTest()
    proc2.attr = 0
    check.equal(proc1, proc2)
    proc2.attr = 1
    check.not_equal(proc1, proc2)
    # Check repr
    check.equal(repr(proc1), "_ProcessingTest")
