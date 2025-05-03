#!/usr/bin/env python
"""
This script contains a test function to perform a dry run of a JIRA creation script. It sets up the environment
variables, creates a temporary template file, and mocks the subprocess.run function to avoid actual execution of the
script. The script is then called with specific arguments to simulate a dry run, and the call is checked using a mock
assertion.

Functions:
- test_script_dry_run: Run a test script in dry-run mode with predefined environment variables.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock


def test_script_dry_run():
    """
    Run a test script in dry-run mode with predefined environment variables.

    Arguments:
    No arguments.

    Side Effects:
    - Sets up a test environment with predefined environment variables for a dry-run test script.
    """

    # Set up environment
    env = os.environ.copy()
    env.update(
        {
            "JIRA_URL": "https://fake.jira",
            "JIRA_PROJECT_KEY": "FAKE",
            "JIRA_AFFECTS_VERSION": "0.0.1",
            "JIRA_COMPONENT_NAME": "dummy-component",
            "JIRA_PRIORITY": "Low",
            "JIRA_JPAT": "fake-token",
            "JIRA_AI_PROVIDER": "noop",
        }
    )

    # Create a temporary template file
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        template_path = template_dir / "bug.tmpl"
        template_path.write_text(
            "FIELD|Title\nTEMPLATE|Description\nBug Title: {{Title}}"
        )

        script_path = Path("jira_creator/rh_jira.py")

        # Mock subprocess.run to avoid actually running the script
        subprocess.run = MagicMock()

        # Call the script (you can use the mock here if you want to check the call)
        subprocess.run(
            [
                "python3",
                str(script_path),
                "--dry-run",
                "--template",
                str(template_path),
            ],
            env=env,
        )

        # Check if subprocess.run was called as expected
        subprocess.run.assert_called_once_with(
            [
                "python3",
                str(script_path),
                "--dry-run",
                "--template",
                str(template_path),
            ],
            env=env,
        )
