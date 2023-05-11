"""Test base class of processing."""

import pytest_check as check

from cliconfig.processing.base import Processing


def test_base_processing() -> None:
    """Test Processing."""
    processing = Processing()
    # Add list_processing to test behavior in general case
    processing.list_processing = [processing]
    flat_dict = {
        "config1.param1": 0,
        "config1.param2": 1,
    }
    check.equal(processing.premerge(flat_dict, [processing]), flat_dict)
    check.equal(processing.list_processing, [processing])
    check.equal(processing.postmerge(flat_dict, [processing]), flat_dict)
    check.equal(processing.list_processing, [processing])
    check.equal(processing.presave(flat_dict, [processing]), flat_dict)
    check.equal(processing.list_processing, [processing])
    check.equal(processing.postload(flat_dict, [processing]), flat_dict)
    check.equal(processing.list_processing, [processing])
