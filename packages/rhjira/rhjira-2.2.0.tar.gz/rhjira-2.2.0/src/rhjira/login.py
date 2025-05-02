import keyring
import getpass
import os
import sys

from keyring.errors import NoKeyringError
from jira import JIRA, JIRAError
from rhjira import util


MAX_RETRIES = 5


def connect2jira(server, token):
    for attempt in range(1, MAX_RETRIES):
        try:
            jira = JIRA(server=server, token_auth=token)
            jira.myself()  # test to see if this works
            util.rhjiratax()
            return jira
        except JIRAError as e:
            if attempt >= MAX_RETRIES:
                print(
                    f"Jira myself test failed (possible permissions or login error): {e.status_code} {e.text}"
                )
                print("Suggestion: Verify that your Red Hat Jira token is valid.")
                sys.exit(1)
            util.rhjiratax()


def login():
    # check the keyring first
    token = None
    try:
        token = keyring.get_password("rhjira", os.getlogin())
    except:
        pass

    if token == None or token == "":
        token = os.getenv("JIRA_TOKEN")
        if token == None or token == "":
            print(
                f"Error: The keyring password could not be read and JIRA_TOKEN was not set."
            )
            sys.exit(1)

    return connect2jira("https://issues.redhat.com", token)


def setpassword():
    token = getpass.getpass("Enter in token (hit ENTER to abort):")
    if token.strip() == "":
        print("No token entered ... aborting")
        sys.exit(1)

    username = os.getlogin()
    print(f"Attempting to save token to {username}'s keyring ....")
    keyring.set_password("rhjira", username, token)
    print("testing login with token ....")

    login()

    print(f"Login succeeded.  Token is saved in keyring as ('{username}' on 'rhjira').")
