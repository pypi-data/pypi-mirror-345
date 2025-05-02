import argparse
import re
import sys

from datetime import datetime
from jira import JIRAError
from rhjira import util


def getnames(fieldlist):
    retstr = ""
    count = 0
    if fieldlist:
        for entry in fieldlist:
            count += 1
            retstr = retstr + f"{entry.name}"
            if count != len(fieldlist):
                retstr = retstr + ", "
    return retstr


def defaultShowText(issue):
    epicname = ""
    epiclink = ""
    parentlink = ""

    if issue.fields.issuetype is not None:
        if issue.fields.issuetype.name == "Epic":
            epicname = issue.fields.customfield_12311141
            parentlink = issue.fields.customfield_12313140
            if parentlink is None:
                parentlink = ""
        else:
            epiclink = issue.fields.customfield_12311140
            if epiclink is None:
                epiclink = ""

    components = getnames(issue.fields.components)

    affectsversions = getnames(issue.fields.versions)

    fixversions = getnames(issue.fields.fixVersions)

    contributors = getnames(issue.fields.customfield_12315950)

    releaseblocker = ""
    if issue.fields.customfield_12319743:
        releaseblocker = issue.fields.customfield_12319743.value

    severity = ""
    if issue.fields.customfield_12316142:
        severity = issue.fields.customfield_12316142.value

    gitpullrequest = ""
    if issue.fields.customfield_12310220:
        for url in issue.fields.customfield_12310220:
            gitpullrequest = url

    assignee = ""
    if issue.fields.assignee is not None:
        assignee = issue.fields.assignee.name

    return f"""{issue.key}: {issue.fields.summary}
===================================
{issue.fields.description}
===================================
Epic Name: {epicname}
Ticket Type: {issue.fields.issuetype}
Status: {issue.fields.status}
Creator: {issue.fields.creator.name}
Assignee: {assignee}
Components: {components}
Affects Versions: {affectsversions}
Fix Versions: {fixversions}
Priority: {issue.fields.priority.name}
Contributors: {contributors}
Release Blocker: {releaseblocker}
Severity: {severity}
Epic Link: {epiclink}
Parent Link: {parentlink}
Git Pull Request: {gitpullrequest}"""


def show(jira):
    # handle arguments
    sys.argv.remove("show")
    parser = argparse.ArgumentParser(
        description="Show basic information on a RH jira ticket"
    )
    args, ticketIDs = parser.parse_known_args()

    if len(ticketIDs) != 1:
        print(f"Error: ticketID not clear or found: {ticketIDs}")
        sys.exit(1)
    ticketID = ticketIDs[0]

    try:
        issue = util.getissue(jira, ticketID)
    except Exception as e:
        print(f"Jira lookup for {ticketID} failed: {e}")
        sys.exit(1)

    outtext = defaultShowText(issue)
    if issue.fields.issuetype.name == "Epic":
        outtext = re.sub(r"^Epic Link:.*\n?", "", outtext, flags=re.MULTILINE)
    else:
        outtext = re.sub(r"^Epic Name:.*\n?", "", outtext, flags=re.MULTILINE)
        outtext = re.sub(r"^Parent Link:.*\n?", "", outtext, flags=re.MULTILINE)

    if issue.fields.issuetype.name not in ["Bug", "Story"]:
        outtext = re.sub(r"^Git Pull Request:.*\n?", "", outtext, flags=re.MULTILINE)

    print(outtext)

    if not issue.fields.comment:
        return

    numcomments = len(issue.fields.comment.comments)
    print(f"--------- {numcomments}  Comments ---------")

    count = 0
    for comment in issue.fields.comment.comments:
        count += 1
        created = datetime.strptime(comment.created, "%Y-%m-%dT%H:%M:%S.%f%z")
        print(f"Comment #{count} | {created.strftime('%c')} | {comment.author.name}")
        print("")
        print(f"{comment.body}")
        print("")
