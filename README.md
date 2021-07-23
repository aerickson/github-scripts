# GitHub-Scripts

A set of scripts for working with/analysis of github orgs/repos

## Requirements
[github3.py](https://github3py.readthedocs.io/en/master/index.html)

## org_repos.py 

```
usage: org_repos.py [-h] [--token TOKEN] [--without-org] [--archived] org

Gets a list of Repos for an Org.

positional arguments:
  org            The GH org to query

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  GH token (PAT) with perms to examine your org
  --without-org  Include the org in the name, 'org/repo-name'
  --archived     Include archived repos. Default is unarchived only.
```

## repo_activity.py

```
usage: repo_activity.py [-h] [--token TOKEN] [--delay DELAY] [--file FILE] [repos ...]

Gets a latest activity for a repo or list of repos

positional arguments:
  repos          list of repos to examine

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  github token with perms to examine your repo
  --file FILE    File of org/repo names, 1 per line
  -i             Give visual output of that progress continues - useful for long runs redirected to a file  
```

## `org_user_membership.py`
```
usage: org_user_membership.py [-h] [--token TOKEN] [--delay DELAY] [-i] org

Gets a list of users for an org with how many repos they're involved with

positional arguments:
  org            The org to examine

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  The PAT to auth with
  --delay DELAY  delay between queries - rate limits, default to 1, should never hit the limit
  -i             Give visual output of that progress continues - useful for long runs redirected to a file
```

## `samlreport.py`
```
usage: samlreport.py [-h] [--url URL] [--token TOKEN] [-f OUTPUT] org

Get SAML account mappings out of a GitHub org

positional arguments:
  org            The org to work on

optional arguments:
  -h, --help     show this help message and exit
  --url URL      the graphql URL
  --token TOKEN  github token with perms to examine your org
  -f OUTPUT      File to store CSV to
```

## `repo_archiver.py`
```
usage: repo_archiver.py [-h] [--token TOKEN] [--file FILE] [-q] [repos ...]

Archive the specified repo, closing out issues and PRs

positional arguments:
  repos          owner/repo to archive

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  PAT to access github. Needs Write access to the repos
  --file FILE    File with "owner/repo" one per line to archive
  -q             DO NOT print, or request confirmations
```

## `repo_unarchiver.py`
```
usage: repo_unarchiver.py [-h] [--token TOKEN] [-q] repo

Reverse archival closing of issues of the specified repo, Note, repo MUST be manually unarchived before this script

positional arguments:
  repo           owner/repo to unarchive

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  PAT to access github. Needs Write access to the repos
  -q             DO NOT print, or request confirmations
```
