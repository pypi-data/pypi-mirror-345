import argparse
import os
import sys

from jira import JIRAError
from rhjira import util


def comment(jira):
    # handle arguments
    sys.argv.remove("comment")
    parser = argparse.ArgumentParser(description="Comment on an RH jira ticket")
    parser.add_argument("-f", "--file", type=str, help="file containing comment")
    parser.add_argument(
        "--noeditor",
        action="store_true",
        help="when set the editor will not be invoked",
    )
    args, ticketIDs = parser.parse_known_args()

    if len(ticketIDs) != 1:
        print(f"Error: ticketID not clear or found: {ticketIDs}")
        sys.exit(1)
    ticketID = ticketIDs[0]

    filename = args.file
    noeditor = args.noeditor

    try:
        issue = util.getissue(jira, ticketID)
    except Exception as e:
        print(f"Jira lookup for {ticketID} failed: {e}")
        sys.exit(1)

    editorText = "# Lines beginning with '#' will be ignored"
    if filename:
        # read the saved contents of $filename
        try:
            with open(filename, "r") as file:
                editorText = file.read()
        except Exception as error:
            print(f"Unable to open {args.template}")
            sys.exit(1)

    savedText = editorText
    if not args.noeditor:
        savedText = util.editFile("rhjira", editorText)
        if len(savedText) == 0:
            print("Empty comment buffer ... aborting.")
            sys.Exit(1)

    try:
        util.addcomment(jira, ticketID, savedText)
    except Exception as e:
        print(f"Failed to add comment to {ticketID}: {e}")
        print("")
        print("Comment text:")
        print(savedText)
        sys.exit(1)

    print(f"https://issues.redhat.com/browse/{ticketID}")
