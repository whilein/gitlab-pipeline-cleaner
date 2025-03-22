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

import datetime
from urllib.parse import quote

import requests
from pydantic import BaseModel


class Project(BaseModel):
    id: int
    path_with_namespace: str
    archived: bool


class Pipeline(BaseModel):
    id: int
    status: str
    updated_at: datetime.datetime


class GitLabAPI:
    url: str
    session: requests.Session

    def __init__(self, url: str, token: str):
        self.url = url

        self.session = requests.Session()

        self.session.headers = {
            'PRIVATE-TOKEN': token
        }

    def _endpoint(self, path: str):
        return self.url + '/api/v4' + path

    def _get(self, path: str, params: dict | None = None):
        response = self.session.get(self._endpoint(path), params=params)
        json = response.json()

        if response.status_code != 200:
            if 'message' in json:
                raise RuntimeError(json['message'])
            elif 'error' in json and 'error_description' in json:
                raise RuntimeError(f"[{json['error']}] {json['error_description']}")
            else:
                raise RuntimeError(f"server returned an error: {response.status_code}")
        return json

    def _paginated(self, path, model, params=None):
        if params is None:
            params = {}

        result = []
        page = 1

        while True:
            json = self._get(path, {'page': page, 'per_page': 100, **params})

            if len(json) == 0:
                break

            for item in json:
                result.append(model(**item))

            page += 1

        return result

    def get_project_pipelines(
            self,
            project_id: int
    ) -> list[Pipeline]:
        return self._paginated('/projects/' + str(project_id) + '/pipelines', Pipeline)

    def delete_pipeline(self, project_id: int, pipeline_id: int):
        self.session.delete(self._endpoint('/projects/' + str(project_id) + '/pipelines/' + str(pipeline_id)))

    def get_group_projects(self, group: str, include_subgroups: bool = False) -> list[Project]:
        return self._paginated('/groups/' + quote(group, safe='') + '/projects', Project,
                               {'include_subgroups': include_subgroups})

    def get_project(self, project: str) -> Project:
        return Project(**self._get('/projects/' + quote(project, safe='')))
