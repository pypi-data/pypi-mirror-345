# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import os
from . import githf
import yaml

# Constants
MACHINE_ORGANIZATION_NAME = 'curious-machine'  # or other organization
PRIVATE_REPO_WITH_TEXT = 'curious_machine'

# Location of the file that is running
WHERE_ARE_WE = os.path.dirname(__file__)

# Repo object
remote_repo = None

try:
    remote_repo = githf.connectto_repo(organization=MACHINE_ORGANIZATION_NAME,
                              repository_name=PRIVATE_REPO_WITH_TEXT,
                              private=True)
    MACHINE_YAML = githf.read_file(repository=remote_repo, file_path='machina.yaml')

except AssertionError as e:
    machina_path = os.path.join(WHERE_ARE_WE, 'machina.yaml')
    with open(machina_path, 'r') as yaml_file:
        MACHINE_YAML = yaml_file.read()

NAME_OF_THE_MACHINE = yaml.load(MACHINE_YAML, Loader=yaml.FullLoader)

# Save the file
# file_path = os.path.join(WHERE_ARE_WE, 'other.yaml')
# with open(file_path, 'w') as yaml_file:
#     yaml.dump(MACHINE_YAML, yaml_file)

__all__ = [
    'NAME_OF_THE_MACHINE',
    'MACHINE_YAML',
    'MACHINE_ORGANIZATION_NAME',
    'remote_repo']
