#!/usr/bin/env python
"""
This file contains a unit test for the 'add_comment' method in the 'cli' module.
The test case simulates a failure scenario by mocking the 'add_comment' method and causing the 'improve_text' method of
'ai_provider' to raise an 'AiError' exception.
The test verifies that the 'AiError' exception is correctly raised and captures the output to check for the expected
error message.

The 'test_add_comment_ai_fail' function mocks the 'add_comment' method for testing purposes without a return value. It
sets up the necessary mocks for 'ai_provider' and verifies that an 'AiError' exception is raised during the test,
capturing and asserting the expected error message.
"""

from unittest.mock import MagicMock, patch

import pytest
from exceptions.exceptions import AiError


def test_add_comment_ai_fail(cli, capsys):
    """
    Mock the add_comment method for testing purposes.
    This function does not have a return value.
    """

    # Mock the add_comment method
    cli.jira.add_comment = MagicMock()

    # Mock the AI provider's improve_text method to simulate an exception
    with patch("commands.cli_add_comment.get_ai_provider") as mock_get_ai_provider:
        # Create a mock AI provider
        mock_ai_provider = MagicMock()
        mock_ai_provider.improve_text.side_effect = AiError("fail")
        mock_get_ai_provider.return_value = mock_ai_provider

        class Args:
            issue_key = "AAP-test_add_comment_ai_fail"
            text = "Comment text"

        with pytest.raises(AiError):
            # Call the method
            cli.add_comment(Args())

        # Capture output and assert
        out = capsys.readouterr().out
        assert "⚠️ AI cleanup failed" in out
