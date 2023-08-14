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
import multiprocessing.pool
import os

import config
import api

from utils import write_timedelta


class Target:
    def get_project_ids(self, gitlab: api.GitLabAPI) -> list[int]:
        pass

    def display_name(self):
        pass

    def priority(self):
        pass


class Project(Target):
    name: str

    def __init__(self, project: config.Project | str):
        if isinstance(project, str):
            self.name = project
        else:
            self.name = project.name

    def priority(self):
        return True

    def display_name(self):
        return 'Project ' + self.name

    def get_project_ids(self, gitlab: api.GitLabAPI) -> list[int]:
        return [gitlab.get_project(self.name).id]


class Group(Target):
    name: str
    recursive: bool
    exclude: list[str]
    archive_behavior: config.ArchiveInclusion

    def __init__(self, group: config.Group | str):
        if isinstance(group, str):
            group = config.Group(name=group)

        self.name = group.name
        self.recursive = group.recursive
        self.exclude = group.exclude
        self.archive_behavior = group.archive_inclusion

    def priority(self):
        return False

    def display_name(self):
        return 'Group ' + self.name

    def get_project_ids(self, gitlab: api.GitLabAPI) -> list[int]:
        return [project.id for project in gitlab.get_group_projects(self.name, self.recursive)
                if project.path_with_namespace not in self.exclude
                and self.archive_behavior.matcher(project.archived)]


def prepare_targets(cfg):
    defaults = cfg.options

    print_options('Default options:', defaults)
    print()
    print('Targets:')

    targets = {}

    for target in cfg.targets:
        target_options = target.options
        target = Project(target.project) if target.project is not None else Group(target.group)

        if target_options is None:
            target_options = defaults
        else:
            if target_options.keep_last is None:
                target_options.keep_last = defaults.keep_last

            if target_options.delete_older_than is None:
                target_options.delete_older_than = defaults.delete_older_than

            if target_options.skip_statuses is None:
                target_options.skip_statuses = defaults.skip_statuses
        print('- ' + target.display_name(), end='')

        if target_options != defaults:
            print_options(':', target_options, ident=2)
        targets[target] = target_options
        print()
    print()

    return targets


def prepare_projects(gitlab, targets):
    print('Searching for project ids..')

    projects = {}

    for target, options in targets.items():
        for project_id in target.get_project_ids(gitlab):
            if project_id in projects and not target.priority():
                continue
            projects[project_id] = options

    print(f'Found {len(projects)} project ids')
    return projects


def main():
    cfg = config.load_config()
    gitlab = api.GitLabAPI(cfg.url, cfg.token)

    targets = prepare_targets(cfg)
    projects = prepare_projects(gitlab, targets)

    pool = multiprocessing.pool.ThreadPool(processes=os.cpu_count() * 2)
    print('Searching for old pipelines..')

    now = datetime.datetime.now(datetime.timezone.utc)

    def get_pipelines_to_delete(item):
        project_id, options = item
        pipelines = gitlab.get_project_pipelines(project_id)
        return [(project_id, pipeline.id) for pipeline in pipelines[options.keep_last:]
                if now - pipeline.updated_at >= options.delete_older_than
                and pipeline.status not in options.skip_statuses]

    pipelines_to_delete = [pipeline for pipelines in pool.map(get_pipelines_to_delete, projects.items()) for pipeline in
                           pipelines]
    print(f'Found {len(pipelines_to_delete)} old pipelines')

    def delete_old_pipelines(pipeline):
        project_id, pipeline_id = pipeline
        gitlab.delete_pipeline(project_id, pipeline_id)

    print('Deleting old pipelines..')
    futures = []

    for pipeline in pipelines_to_delete:
        futures.append(pool.apply_async(delete_old_pipelines, args=(pipeline,)))

    for future in futures:
        future.get()

    print('Old pipelines were deleted')
    pool.close()


def print_options(title: str, options: config.Options, ident: int = 0):
    print(title)
    print(' ' * ident, end='')
    if options.keep_last == 0 and options.delete_older_than.total_seconds() <= 0:
        print('Delete all pipelines')
    elif options.keep_last == 0:
        print(f'Delete all pipelines older than {write_timedelta(options.delete_older_than)}')
    elif options.delete_older_than.total_seconds() <= 0:
        print(f'Keep last {options.keep_last} pipelines')
    else:
        print(f'Delete pipelines older than {write_timedelta(options.delete_older_than)}, '
              f'but keep at least {options.keep_last}')


if __name__ == '__main__':
    main()
