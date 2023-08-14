#     Copyright 2023 Whilein
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import os
from enum import Enum
from pathlib import Path
from datetime import timedelta
from typing import Any

import yaml
from pydantic import BaseModel, model_validator, field_validator

from utils import read_timedelta

CONFIG_PATH = Path(os.environ.get('CONFIG_PATH', 'config.yml'))
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class Options(BaseModel):
    keep_last: int = None
    delete_older_than: timedelta = None
    skip_statuses: list[str] = None

    @field_validator('delete_older_than', mode='before')
    @classmethod
    def decode(cls, value: str):
        if value is None:
            return None

        return read_timedelta(value)


class DefaultOptions(Options):
    keep_last: int
    delete_older_than: timedelta
    skip_statuses: list[str]


class ArchiveInclusion(Enum):
    ONLY = 'only', lambda archived: archived
    INCLUDE = 'include', lambda archived: True
    EXCLUDE = 'exclude', lambda archived: not archived

    def __new__(cls, value, matcher):
        enum = object.__new__(cls)
        enum._value_ = value
        enum.matcher = matcher
        
        return enum


class Group(BaseModel):
    name: str
    recursive: bool = False
    exclude: list[str] = []
    archive_inclusion: ArchiveInclusion = ArchiveInclusion.INCLUDE


class Project(BaseModel):
    name: str


class Target(BaseModel):
    project: str | Project = None
    group: str | Group = None
    options: Options = None

    @model_validator(mode='before')
    @classmethod
    def ensure_project_or_group(cls, data: Any) -> Any:
        if ('project' not in data) == ('group' not in data):
            raise ValueError('either a project or a group is required')
        return data


class Config(BaseModel):
    url: str
    token: str
    options: DefaultOptions
    targets: list[Target]


def load_config() -> Config:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open('r') as f:
            config = yaml.safe_load(f)
    else:
        with CONFIG_PATH.open('w') as f:
            config = {
                'url': 'https://gitlab.com',
                'token': '',
                'options': {
                    'skip_statuses': ['created', 'waiting_for_resources', 'preparing', 'pending', 'running'],
                    'keep_last': 20,
                    'delete_older_than': '30d'
                },
                'targets': [
                    {
                        'project': 'mygroup/myproject',
                        'options': {
                            'delete_older_than': '7d'
                        }
                    },
                    {
                        'group': 'mygroup'
                    },
                    {
                        'group': {
                            'name': 'mygroup',
                            'excludes': [
                                'mygroup/myproject'
                            ]
                        }
                    }
                ]
            }

            yaml.safe_dump(config, f, sort_keys=False)

    return Config(**config)
