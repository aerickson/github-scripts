#!/usr/bin/env python
"""
Script to perform a search of supplied orgs, returning the repo list that return positives
"""

import configparser
import sys
from time import sleep

from github3 import exceptions as gh_exceptions
from github3 import login

from github_scripts import utils


def parse_arguments():
    """
    Look at the first arg and handoff to the arg parser for that specific
    """
    parser = utils.GH_ArgParser(
        description="Get file search results for an org, returning repo list.  "
        "e.g. if you want 'org:<ORGNAME> filename:<FILENAME> <CONTENTS>', "
        "then you just need 'filename:<FILENAME> <CONTENTS>' "
        "and then list the orgs to apply it to.  "
        "Note: There's a pause of ~10 seconds between org searches "
        "due to GitHub rate limits - add a -v if you want notice printed that it's waiting"
    )
    parser.add_argument(
        "--query", type=str, help="The query to run, without orgs", action="store", required=True
    )
    parser.add_argument(
        "--note-archive",
        help="if specified, will add archival status of the repo to the output, this will slow things down and use more API calls",
        action="store_true",
        dest="note_archive",
    )
    parser.add_argument("orgs", type=str, help="The org to work on", action="store", nargs="*")
    parser.add_argument(
        "--orgini",
        help='use "orglist.ini" with the "orgs" ' "entry with a csv list of all orgs to check",
        action="store_const",
        const="orglist.ini",
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        help="Verbose - Print out that we're waiting for rate limit reasons",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-f",
        dest="print_file",
        help="Print out file level responses rather than repo level",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        dest="time",
        default=10,
        type=int,
        help="Time to sleep between searches, in seconds, should be 10s or more",
    )
    args = parser.parse_args()
    if args.orgs == [] and args.orgini is None:
        raise SystemExit("You must specify either an org or an orgini")
    return args


def main():
    """
    Taking in the query and list of orgs, run the search,
    print out the org name and the list of repos affected.
    """
    args = parse_arguments()
    do_search(args)


def do_search(args):
    # Read in the config if there is one
    orglist = []
    if args.orgini is not None:
        config = configparser.ConfigParser()
        config.read(args.orgini)
        orglist = config["GITHUB"]["orgs"].split(",")
    else:
        orglist = args.orgs

    gh_sess = login(token=args.token)
    if not gh_sess:
        raise SystemExit("Failed to get GitHub API session")
    length = len(orglist)  # Used to determine when to pause
    if args.print_file:
        print("Files found:")
        if args.note_archive:
            print("Repo,Visibility,Archived,Filename")
        else:
            print("Repo,Visibility,Filename")
    else:
        if args.note_archive:
            print("Repos found: org/repo/is_archived")
        else:
            print("Repos found: org/repo")

    for org in orglist:
        try:
            search = gh_sess.search_code(f"org:{org} {args.query}", text_match=False)
            repos = set()
            files = []
            for result in search:
                repo_fullname = "{org}/{result.repository.name}"
                archived = "<unknown>"
                if args.note_archive:
                    fullrepo = gh_sess.repository(owner=org, repository=result.repository.name)
                    if fullrepo:
                        archived = fullrepo.archived
                    else:
                        print("Couldn't get archive status for {repo_fullname}", file=sys.stderr)
                    repos.add(f"{repo_fullname}/{archived}")
                else:
                    repos.add(f"{org}/{result.repository.name}")
                if result.repository.private:
                    vistext = "Private"
                else:
                    vistext = "Public"
                if args.note_archive:
                    files.append(f"{result.repository},{vistext},{archived},{result.path}")
                else:
                    files.append(f"{result.repository},{vistext},{result.path}")
                utils.spinner(org)
                sleep(args.time / 20)
            utils.spinner(org, end_spinner=True)
            if args.print_file and files:
                for line in files:
                    print(line)
            elif repos:
                print("\n".join(repos))

        except gh_exceptions.UnprocessableEntity:
            print(
                f"org: {org} Failed, likely due to lack of repos in the org",
                file=sys.stderr,
            )
        finally:
            length -= 1
            if length > 0:
                if args.verbose:
                    print(
                        f"Sleeping {args.time} seconds per GitHub's secondary rate limits",
                        file=sys.stderr,
                    )
                # per https://docs.github.com/en/rest/guides/best-practices-for-integrators#dealing-with-secondary-rate-limits
                sleep(args.time)


if __name__ == "__main__":
    main()
