import rhjira
import pprint
import sys

from jira import JIRAError


def usage():
    print("Usage:")
    print("  rhjira [flags] [command]")
    print(" ")
    print("Available Commands:")
    print("  comment     Comment on a jira ticket on https://issues.redhat.com")
    print("  create      Create a jira ticket on https://issues.redhat.com")
    print("  dump        Dump jira issue variables.")
    print("  edit        Edit a jira ticket on https://issues.redhat.com")
    print("  help        Help about any command")
    print("  list        list issues")
    print("  show        Edit a jira ticket on https://issues.redhat.com")
    print(
        "  settoken    Save a jira token to the keyring (more secure than using $JIRA_TOKEN)"
    )
    print(" ")
    print("For help on individual commands, execute rhjira [command] --help")
    sys.exit(1)


def main():
    if len(sys.argv) <= 1:
        usage()

    if sys.argv[1] != "settoken":
        try:
            jira = rhjira.login()
        except JIRAError as e:
            print(f"Jira login failed: {e.status_code} {e.text}")
            sys.exit(1)

    match sys.argv[1]:
        case "comment":
            rhjira.comment(jira)
        case "close":
            rhjira.edit(jira)
        case "create":
            rhjira.create(jira)
        case "dump":
            rhjira.dump(jira)
        case "edit":
            rhjira.edit(jira)
        case "list":
            rhjira.list(jira)
        case "settoken":
            rhjira.setpassword()
        case "show":
            rhjira.show(jira)
        case _:
            usage()


if __name__ == "__main__":
    main()
