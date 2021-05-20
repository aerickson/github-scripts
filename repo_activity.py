#!/usr/bin/env python
"""
Script for determining activity levels of a repo
Used to help determination for archiving/moving repos that aren't active
"""

import argparse
from getpass import getpass
from datetime import datetime
from github3 import login

def parse_args():
    """
    Parse the command line.  Required commands is the name of the repo, and the org
    Will accept many repos on the command line
    Detects if no PAT is given, asks for it.
    :return: Returns the parsed CLI datastructures.
    """

    parser = argparse.ArgumentParser(description=
                    "Gets a latest activity for a repo or list of repos")
    parser.add_argument('--org', help='Name of the org the repos belong to',
                    action='store', required=True)
    parser.add_argument('repos',
                    help='list of repos to examine',
                    action='store', nargs='*')
    parser.add_argument('--token', help='github token with perms to examine your repo',
                    action='store')
    parser.add_argument('--file', help="File of repo names, 1 per line",
                    action = 'store')

    args = parser.parse_args()
    if args.repos is None and args.file is None:
        raise Exception("Must have either a list of repos, OR a file to read repos from")
    if args.token is None:
        args.token = getpass('Please enter your GitHub token: ')
    return args

def repo_activity(gh_sess, org, repo, printout=True, header=True):
    """
    Look at the repo, and return activity, with the date of their latest commit,
        or no commit, over the last year
    :param gh_sess: an initialized github session
    :param org: the organization (or owner) name
    :param repo: the repo name
    :param printout: Print it out here - defaults True, if False, just return the list.
    :param header: Should I print a descriptive header?
    :return: list, repo, created_date, last admin update, last push, last commit
    """
    short_repo = gh_sess.repository(org, repo)

    commitlist = {}
    repo = short_repo.refresh()
    topdate = 0
    commits = repo.commit_activity()
    for week in commits:
        if week['total'] != 0:
            if week['week'] > topdate:
                topdate = week['week']
    commitval = 0
    if topdate == 0:
        #no commits found, update list as apropos
        commitval = 'None'
    else:
        commitval = datetime.fromtimestamp(topdate)
    commitlist[repo.name] = {'created_at':repo.created_at,
                            'updated_at':repo.pushed_at,
                            'admin_update':repo.updated_at,
                            'last_commit': commitval,
                            'archived':repo.archived}

    if printout:
        if header:
            print("Repo, Created, Updated, Admin_update, Last_commit")
        for repo in commitlist:
            if commitlist[repo]['archived']:
                print(f"{repo}, ARCHIVED")
            else:
                print(f"{repo},{commitlist[repo]['created_at']},{commitlist[repo]['updated_at']},"
                        f"{commitlist[repo]['admin_update']},{commitlist[repo]['last_commit']}")
    return commitlist

def main():
    """
    Given a list of repos, and an org, get some data around last use
    """

    args = parse_args()

    header = True
    repolist = []
    if args.repos != []:
        repolist = args.repos
    else:
        # Rip open the file, make a list
        txtfile = open(args.file, 'r')
        repolist = txtfile.readlines()
        txtfile.close()

    gh_sess = login(token=args.token)

    for repo in repolist:
        repo_activity(gh_sess, args.org, repo.strip(), header=header)
        if header:
            header = False #We only want a header on the first line

if __name__ == '__main__':
    main()
