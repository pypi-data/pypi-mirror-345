# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import environ
from github import Github, UnknownObjectException
from urllib3 import disable_warnings


github_token    = environ.get('GITHUB_TOKEN', '')
github_name     = environ.get('GITHUB_NAME', '')
github_email    = environ.get('GITHUB_EMAIL', '')

# The useless urllib3 warning is too maddening for an ordinary human being.
disable_warnings()


# Repo
def connectto_repo(organization=None,
                   repository_name=None,
                   private=False):
    """
    Establish connection with a repository.
    Return 'None' if connection fails.
    """
    gh = Github(github_token, verify=False)
    if organization:
        org = gh.get_organization(organization)
        try:
            repo = org.get_repo(f'{repository_name}')
        except UnknownObjectException:
            # print('Can not connect YOU to this repo in this organization')
            repo = None
        return repo
    else:
        user = gh.get_user()
        try:
            repo = user.get_repo(repository_name)
        except UnknownObjectException:
            # print('Can not connect YOU to this repo')
            repo = None
        return repo


def read_file(repository,
              file_path):
    """ Read a file in a repository
        file_path: path to the file formatted as
        'directory_in_repo/subdirectory/file.ext'
    """
    try:
        # Get the file if it exists
        ingested_file = repository.get_contents(file_path)
        content = ingested_file.decoded_content.decode("utf-8")

    except UnknownObjectException:
        # The file doesn't exist
        # print('The file does not exist')
        content = ''

    return content
