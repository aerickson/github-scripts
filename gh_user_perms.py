#!/usr/bin/env python
"""
Script to report on user permissions in an org (and optionally a specific repo).

Note - github API reports perms for users as if the team is the user...
So there's no indication here if the perm is to the user or a team they
belong to.
"""

import os
import sys

import alive_progress
from github3 import login

from github_scripts import utils


def parse_args():
    """
    Parse the command line.  Required commands is the name of the org
    :return: Returns the parsed CLI datastructures.
    """

    parser = utils.GH_ArgParser(description="Report on a user's permissions in an org.")
    parser.add_argument("user", help="Single user to examine in the org")
    parser.add_argument("org", help="The org to examine")
    parser.add_argument(
        "--no-archive",
        help="Omit archived repos from the response",
        action="store_true",
        dest="omit_archive",
    )
    # TODO: add verbose to show the raw datastructure?
    parser.add_argument("--repo", help="Single repo to examine in the org")
    args = parser.parse_args()

    return args


# checks for "repo" and "*repo" in a list
# returns match, if no match then None
def check_if_repo_present(repo, a_list):
    if f"*{repo}" in a_list:
        return f"*{repo}"
    if repo in a_list:
        return repo
    return None


def main():
    """
    Parse the args, connect to github, get the list of users in the org.
    Then go through the repos and update the users with usage counts.
    {user:{role: orgrole, team:count, repo:count}}
    leaving team in for now - but not updating it
    """
    args = parse_args()

    # we disable certain output if the terminal isn't interactive
    session_is_interactive = False
    if os.isatty(sys.stdout.fileno()):
        session_is_interactive = True

    userlist = {}
    # function-based code
    gh_sess = login(token=args.token)
    # object-based code
    ghq = utils.GHPermsQuery()
    ghq.init_gh_session(token=args.token)

    org = gh_sess.organization(args.org)

    # If a user was specified, just do that one, else, list all org members
    if args.user is None:
        memberlist = org.members(role="member")
    else:
        memberlist = [gh_sess.user(args.user)]
    for member in memberlist:
        userlist[member.login] = {
            "role": "member",
            "privpull": [],
            "privpush": [],
            "privadmin": [],
            "pubpull": [],
            "pubpush": [],
            "pubadmin": [],
        }

    if args.user is None:
        adminlist = org.members(role="admin")
        for admin in adminlist:
            userlist[admin.login] = {
                "role": "admin",
                "privpull": [],
                "privpush": [],
                "privadmin": [],
                "pubpull": [],
                "pubpush": [],
                "pubadmin": [],
            }

    # great, we have initialized our lists - now to go through the repos

    # retrieve list of repos
    # If a repo is specified, just look at that one, otherwise all of them in the org.
    if args.repo is None:
        # TESTING
        # repolist = org.repositories(number=100)
        repolist = org.repositories()
    else:
        repolist = [gh_sess.repository(args.org, args.repo)]

    with alive_progress.alive_bar(
        manual=True,
        title="fetching list of repos",
        file=sys.stderr,
        force_tty=True,  # force_tty because we are outputting to stderr now
    ) as bar:
        # materialize the iterator so we can get a count
        repolist = list(repolist)
        bar(1)

    # FIXME Should I pull out "-ghsa-" repos - they NEVER find perms right.
    # Alternatively, just silently pass the NotFoundError?  (don't like that at first blush)
    userlist = ghq.update_userlist_with_permission_data(
        userlist, repolist, user=args.user, session_is_interactive=session_is_interactive
    )

    # debugging
    # TODO: only show if -v or something
    # print(userlist)

    # print header
    print("user,org,repo,role,access")

    # should only be one username...
    # TODO: complain (earlier) if more than one?
    for username, data in userlist.items():
        # figure out different way of iterating...
        # - need this as way of checking data structure currently
        # - generate new data structure?
        for repo in repolist:
            if repo.archived and args.omit_archive:
                continue  # Skip this repo
            access_string = ""
            tmp_list = []

            # handle role
            access_level = ""
            if data["role"] == "member":
                access_level = "member"
            elif data["role"] == "admin":
                access_level = "admin"
            elif data["role"] == "outside":
                access_level = "outside"
            else:
                raise "shouldn't be here"

            # TODO: don't discard the fact that the repo is archived (if it is)
            #   - requires data structure tweaks
            if check_if_repo_present(repo.name, data["pubpull"]):
                tmp_list.append("pubpull")
            if check_if_repo_present(repo.name, data["pubpush"]):
                tmp_list.append("pubpush")
            if check_if_repo_present(repo.name, data["pubadmin"]):
                tmp_list.append("pubadmin")
            if check_if_repo_present(repo.name, data["privpull"]):
                tmp_list.append("privpull")
            if check_if_repo_present(repo.name, data["privpush"]):
                tmp_list.append("privpush")
            if check_if_repo_present(repo.name, data["privadmin"]):
                tmp_list.append("privadmin")

            access_string = ",".join(tmp_list)

            if access_string != "":
                print(f'{username},{args.org},{repo.name},{access_level},"{access_string}"')


if __name__ == "__main__":
    main()
