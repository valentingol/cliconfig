# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Tests for dict routines."""
import pytest
import pytest_check as check

from cliconfig._logger import create_logger


def test_create_logger(
    caplog: pytest.CaptureFixture,
    capsys: pytest.CaptureFixture,
) -> None:
    """Test create_logger."""
    logger = create_logger()
    logger.info("This is an info message.")
    check.is_true("INFO     cliconfig._logger:test_logger.py:" in caplog.text)
    check.is_true(" This is an info message." in caplog.text)
    check.is_true("INFO - This is an info message." in capsys.readouterr().out)
    logger.warning("This is a warning message.")
    check.is_true("WARNING  cliconfig._logger:test_logger.py:" in caplog.text)
    check.is_true(" This is a warning message." in caplog.text)
    check.is_true("WARNING - This is a warning message." in capsys.readouterr().out)
