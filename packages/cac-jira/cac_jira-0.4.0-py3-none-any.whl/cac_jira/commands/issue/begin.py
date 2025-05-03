# #!/usr/bin/env python
# pylint: disable=no-member, broad-exception-caught

from cac_jira.commands.issue import JiraIssueCommand


class IssueBegin(JiraIssueCommand):
    """
    Command class for transitioning Jira issues to "In Progress".
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add common arguments first
        super().define_arguments(parser)
        parser.add_argument(
            "-i",
            "--issue",
            help="Issue to transition to In Progress",
            default=None,
            required=True,
        )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Transitioning Jira issue %s to In Progress", args.issue)

        # Get the issue
        issue = self.jira_client.issue(args.issue)
        if not issue:
            self.log.error("Issue not found")
            return

        # Get all available transitions for the issue
        transitions = self.jira_client.transitions(issue)

        # Find the transition ID where name is "In Progress"
        in_progress_id = None
        for transition in transitions:
            if transition['name'] == "In Progress":
                in_progress_id = transition['id']
                self.log.debug("Found 'In Progress' transition with ID: %s", in_progress_id)
                break

        if not in_progress_id:
            self.log.error("No 'In Progress' transition found for this issue")
            # List all available transitions
            self.log.info("Available transitions:")
            for transition in transitions:
                self.log.info("  - %s (ID: %s)", transition['name'], transition['id'])
            return

        # Transition the issue to "In Progress"
        try:
            self.jira_client.transition_issue(issue, in_progress_id)
            self.log.info("Issue %s transitioned to In Progress", issue.key)
        except Exception as e:
            self.log.error("Failed to transition issue: %s", str(e))
