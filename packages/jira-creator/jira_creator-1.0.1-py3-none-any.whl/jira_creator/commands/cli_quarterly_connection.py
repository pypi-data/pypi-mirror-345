#!/usr/bin/env python
"""
This script generates a quarterly employee report by querying JIRA for issues assigned to the current user.
It includes a main function, `cli_quarterly_connection`, which retrieves JIRA issues from the last 90 days,
processes the information, and handles exceptions related to JIRA searches.

Functions:
- `cli_quarterly_connection`: Constructs a quarterly report by querying JIRA for issues created, resolved, updated,
or commented on by the current user within the last 90 days.

Arguments:
- `jira`: An instance of `JiraClient` for accessing JIRA issues.

Exceptions:
- Raises `QuarterlyConnectionError` if there are issues with the JIRA search operation.

Side Effects:
- Outputs "Building employee report" to the console and prints the summarized report.

Note:
- The function filters out issues related to CVEs and prints relevant summaries to the console.
"""

import time
from typing import List, Optional

from core.env_fetcher import EnvFetcher
from exceptions.exceptions import QuarterlyConnectionError
from providers import get_ai_provider
from providers.ai_provider import AIProvider
from rest.client import JiraClient
from rest.prompts import IssueType, PromptLibrary


def cli_quarterly_connection(jira: JiraClient) -> Optional[bool]:
    """
    Builds a quarterly employee report based on JIRA issues assigned to the current user.

    Arguments:
    - jira: A JIRA API client for interacting with JIRA issues.

    Exceptions:
    - Raises exceptions if there are any issues with searching JIRA issues.

    Side Effects:
    - Prints "Building employee report".

    Note: This function fetches JIRA issues created, resolved, updated, or commented on by the current user within the
    last 90 days.
    """

    try:
        print("Building employee report")
        jql: str = (
            "(created >= -90d OR resolutionDate >= -90d OR"
            " updated >= -90d OR comment ~ currentUser()) AND assignee = currentUser()"
        )
        issues: List[dict] = jira.search_issues(jql)

        if issues is None or len(issues) == 0:
            print("❌ No issues found for the given JQL.")
            return None

        system_prompt: str = PromptLibrary.get_prompt(IssueType.QC)

        qc_input: str = ""
        for issue in issues:
            key: str = issue["key"]
            fields: dict = issue["fields"]
            qc_input += "========================================================\n"
            summary: str = fields.get("summary") or ""
            description: str = jira.get_description(key) or ""
            print("Fetched: " + summary)
            time.sleep(2)
            if "CVE" in summary:
                print("Not adding CVE to analysis")
                continue
            qc_input += summary + "\n"
            qc_input += description + "\n"

        print(qc_input)

        print("Manager churning:")
        ai_provider: AIProvider = get_ai_provider(EnvFetcher.get("JIRA_AI_PROVIDER"))
        print(ai_provider.improve_text(system_prompt, qc_input))

        return True
    except QuarterlyConnectionError as e:
        print(e)
        raise QuarterlyConnectionError(e) from e
