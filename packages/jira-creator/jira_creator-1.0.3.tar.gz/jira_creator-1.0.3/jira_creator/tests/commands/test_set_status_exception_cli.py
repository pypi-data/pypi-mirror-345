#!/usr/bin/env python
"""
This file contains a unit test function to test an exception scenario for the set_status method. The test mocks the
set_status method to raise a SetStatusError and verifies that the appropriate error message is printed. The test
function uses pytest for assertions and captures the output using capsys.

test_set_status_exception(cli, capsys):
Set an exception for the set_status method to be raised when called.

Arguments:
- cli: An object representing the CLI.
- capsys: A fixture for capturing stdout and stderr outputs.

Exceptions:
- SetStatusError: Raised when the set_status method encounters an error with the message "bad status".
"""

from unittest.mock import MagicMock

import pytest
from exceptions.exceptions import SetStatusError


def test_set_status_exception(cli, capsys):
    """
    Set an exception for the set_status method to be raised when called.

    Arguments:
    - cli: An object representing the CLI.
    - capsys: A fixture for capturing stdout and stderr outputs.

    Exceptions:
    - SetStatusError: Raised when the set_status method encounters an error with the message "bad status".
    """

    # Mock the set_status method to simulate an exception
    cli.jira.set_status = MagicMock(side_effect=SetStatusError("bad status"))

    class Args:
        issue_key = "AAP-test_set_status_exception"
        status = "Invalid"

    with pytest.raises(SetStatusError):
        # Call the method
        cli.set_status(Args())

    # Capture the output
    out = capsys.readouterr().out

    # Assert that the correct error message was printed
    assert "❌ Failed to update status" in out
