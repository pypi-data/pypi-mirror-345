import json
import os
import re
import shlex
import subprocess
import time

from jira import JIRAError
from datetime import datetime

MAX_RETRIES = 5


def convertdescription(description):
    return description.replace(r"\n", "\n")


def dumpissue(issue):
    print(json.dumps(issue.raw, indent=4))


def rhjiratax():
    # RH's Jira instance has a 2/second/node rate limit.  To avoid
    # this the code has to implement a 1 second delay at times.
    time.sleep(1)


def removecomments(intext):
    # remove all lines beginning with # (hash)
    outtext = re.sub(r"^#.*\n", "", intext, flags=re.MULTILINE)
    return outtext


def isGitRepo():
    try:
        with open(os.devnull, "w") as devnull:
            subprocess.check_call(
                ["git", "-C", "./", "rev-parse", "--is-inside-work-tree"],
                stdout=devnull,
                stderr=devnull,
            )
        return True
    except subprocess.CalledProcessError:
        return False


def geteditor():
    editor = os.environ.get("GIT_EDITOR") or os.environ.get("EDITOR") or "vi"
    if not editor:
        print("Could not determine editor.  Please set GIT_EDITOR or EDITOR.")
        sys.exit(1)

    return editor


def editFile(fileprefix, message):
    editor = geteditor()
    command = shlex.split(editor)

    if isGitRepo():
        workingdir = os.getcwd()
    else:
        workingdir = "/tmp"

    filename = workingdir + "/" + f"{fileprefix}_EDITMSG"

    command.append(filename)

    # prepopulate the file with message
    if message:
        with open(filename, "w") as file:
            file.write(message)

    # open the editor and save the contents in $filename
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Editor open failed with: {e}")
        os.remove(filename)
        sys.exit(1)

    # read the saved contents of $filename
    with open(filename, "r") as file:
        intext = file.read()

    # cleanup
    os.remove(filename)

    intext = removecomments(intext)
    intext = re.sub(r"^#.*\n", "", intext, flags=re.MULTILINE)

    return intext


def dump_any(field, value):
    if value == None:
        return ""

    # customfield_12316840/"Bugzilla Bug"
    if field.id == "customfield_12316840":
        return value.bugid

    return value


def dump_user(field, user):
    return f"{user.displayName} <{user.emailAddress}>"


def dump_version(field, version):
    return version.name


def dump_component(field, component):
    return component.name


def dump_issuelink(field, issuelink):
    if hasattr(issuelink, "outwardIssue"):
        return f"{issuelink.type.outward} https://issues.redhat.com/browse/{issuelink.outwardIssue.key}"
    else:
        return f"{issuelink.type.inward} https://issues.redhat.com/browse/{issuelink.inwardIssue.key}"


def dump_attachment(field, attachment):
    # this returns an actual URL.  A filename could be returned as
    # attachment.filename
    return attachment.content


def dump_group(field, group):
    return group.name


def dump_array(field, array):
    # customfield_12323140/"Target Version"
    if field.id == "customfield_12323140":
        return dump_version(field, array)
    # customfield_12315950/"Contributors"
    if field.id == "customfield_12315950":
        userstr = ""
        count = 0
        for cf in array:
            count += 1
            user = cf
            userstr = userstr + dump_user(field, user)
            if count != len(array):
                userstr = userstr + ", "
        return userstr

    if array == []:
        return ""

    if field.schema["items"] and field.schema["items"] != "worklog":
        retstr = ""
        count = 0
        for entry in array:
            count += 1
            match field.schema["items"]:
                case "attachment":
                    retstr = retstr + dump_attachment(field, entry)
                case "component":
                    retstr = retstr + dump_component(field, entry)
                case "group":
                    # for some reason 'group' is defined as an array, but it doesn't
                    # appear to be an array (at least in the cases I've found)
                    retstr = retstr + dump_group(field, entry)
                case "issuelinks":
                    retstr = retstr + dump_issuelink(field, entry)
                case "option":
                    retstr = retstr + dump_option(field, entry)
                case "string":
                    retstr = retstr + entry
                case "user":
                    # does this fix contributors above?
                    retstr = retstr + dump_user(field, entry)
                case "version":
                    retstr = retstr + dump_version(field, entry)
                case "worklog":
                    # currently not used in RH
                    return ""
                case _:
                    # To debug this, do a 'rhjira dump --json <ticketID>', and
                    # use that to find the specific structure contents.
                    print(f"PRARIT unhandled array {field.schema['items']}")
                    return ""
            if count != len(array):
                retstr = retstr + ", "
        return retstr

    return ""


def dump_securitylevel(field, security):
    return security.description


def dump_option(field, option):
    return option.value


def dump_optionwithchild(field, option):
    if hasattr(option, "child"):
        return f"{option.value} - {option.child.value}"
    return f"{option.value}"


def dump_votes(field, votes):
    return votes.votes


def dump_progress(field, progress):
    return f"{progress.progress}%"


def dump_watches(field, watches):
    if not watches.isWatching:
        return "0"
    return watches.watchCount


def dump_comment(field, comment):
    creator = dump_user({}, comment.author)
    timestamp = convert_jira_date(comment.created)
    return f'"Created by {creator} at {timestamp} :\\n{comment.body}\\n\\n"'


def dump_comments(field, comments):
    retstr = ""
    count = 0
    for comment in comments:
        count += 1
        retstr = retstr + dump_comment({}, comment)
        if count != len(comments):
            retstr = retstr + ", "
    return retstr


def convert_jira_date(datestr):
    try:
        # 2024-09-03 11:34:05
        date = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%f%z")
    except:
        # 2025-04-30
        try:
            date = datetime.strptime(datestr, "%Y-%m-%d")
        except:
            print(f"ERROR: undefined date format {datestr}")
            sys.exit(1)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def dict_to_struct(data):
    return type("", (object,), data)()


def evaluatefield(field, value, noescapedtext):
    schema = dict_to_struct(field.schema)
    match schema.type:
        case "any":
            # "Git Pull Request"
            if field.id == "customfield_12310220":
                retstr = ""
                count = 0
                for v in value:
                    count += 1
                    retstr = retstr + v
                    if count != len(value):
                        retstr += ", "
                return retstr
            return dump_any(field, value)
        case "array":
            if value is None:
                return ""
            else:
                return dump_array(field, value)
        case "date":
            if value is None:
                return ""
            else:
                return convert_jira_date(value)
        case "datetime":
            # A subtlety of date and datetime seem to be that date
            # can be None.  datetime is used for fields that MUST
            # have a date as far a I can tell.  The None check
            # below may not be strictly necessary?
            if value is None:
                return ""
            else:
                date = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
                # 2024-09-03 11:34:05
                return date.strftime("%Y-%m-%d %H:%M:%S")
        case "issuelinks":
            if value is None:
                return ""
            else:
                return dump_issuelink(field, value)
        case "issuetype":
            return value
        case "number":
            if value is None:
                return "0"
            else:
                return value
        case "sd-approvals":
            # cannot find any tickets with this field set.  For now
            # just return an empty string
            return ""
        case "sd-customerrequesttype":
            # cannot find any tickets with this field set.  For now
            # just return an empty string
            return ""
        case "sd-servicelevelagreement":
            # cannot find any tickets with this field set.  For now
            # just return an empty string
            return ""
        case "securitylevel":
            if value is None:
                return ""
            else:
                return dump_securitylevel(field, value)
        case "string":
            if value is None:
                return ""
            else:
                if noescapedtext:
                    return value
                else:
                    return value.replace("\n", "\\n")
        case "timetracking":
            # Not currently used.  Will have to adjust this code if it is used.
            return ""
        case "option":
            if value is None:
                return ""
            else:
                return dump_option(field, value)
        case "option-with-child":
            if value is None:
                return ""
            else:
                return dump_optionwithchild(field, value)
        case "priority":
            if value is None:
                return ""
            else:
                return value
        case "project":
            if value is None:
                return ""
            else:
                return value
        case "progress":
            if value is None:
                return ""
            else:
                return dump_progress(field, value)
        case "resolution":
            if value is None:
                return ""
            else:
                return value
        case "status":
            if value is None:
                return ""
            else:
                return value
        case "user":
            if value is None:
                return ""
            else:
                return dump_user(field, value)
        case "version":
            if value is None:
                return ""
            else:
                return dump_version(field, value)
        case "votes":
            if value is None:
                return ""
            else:
                return dump_votes(field, value)
        case "watches":
            if value is None:
                return ""
            else:
                return dump_watches(field, value)
        case "comments-page":
            return dump_comments(field, value.comments)
        case _:
            print(
                f"ERROR undefined field type FIELD[{field.name}|{field_name}]: ",
                schema.type,
                value,
            )


def getfieldlist(jirafields, userfields):
    # generate a list of fields
    fields = []
    if not userfields:
        for fielddict in jirafields:
            field = dict_to_struct(fielddict)
            fields.append(field)
        return fields

    for userfield in userfields:
        for fielddict in jirafields:
            field = dict_to_struct(fielddict)
            if field.id == userfield or field.name == userfield:
                fields.append(field)
                continue
    return fields


MAX_RETRIES = 5

class RHJiraFetchError(Exception):
    pass

def getissue(jira, ticketID):
    for attempt in range(1, MAX_RETRIES):
        try:
            issue = jira.issue(ticketID)
            rhjiratax()
            return issue
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e


def getfields(jira):
    for attempt in range(1, MAX_RETRIES):
        try:
            fields = jira.fields()
            rhjiratax()
            return fields
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e

def addcomment(jira, ticketID, savedText):
    for attempt in range(1, MAX_RETRIES):
        try:
            jira.add_comment(ticketID, savedText)
            return
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e

def createissue(jira, fields):
    for attempt in range(1, MAX_RETRIES):
        try:
            return jira.create_issue(fields=fields)
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e

def gettransitions(jira, issue):
    for attempt in range(1, MAX_RETRIES):
        try:
            transitions = jira.transitions(issue)
            rhjiratax()
            return transitions
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e

def transitionissue(jira, issue, stateID):
    for attempt in range(1, MAX_RETRIES):
        try:
            jira.transition_issue(issue, stateID)
            return
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e

def assignissue(jira, issue, assignee):
    for attempt in range(1, MAX_RETRIES):
        try:
            jira.assign_issue(issue, assignee)
            return
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e

def searchissues(jira, searchstring, maxentries):
    for attempt in range(1, MAX_RETRIES):
        try:
            return jira.search_issues(searchstring, maxResults=maxentries)
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                raise RHJiraFetchError(f("JIRAError {e.status_code}: {e.text}")) from e
