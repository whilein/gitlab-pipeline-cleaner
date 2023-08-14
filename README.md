# gitlab-pipeline-cleaner

<div align="center">
  <a href="https://github.com/whilein/gitlab-pipeline-cleaner/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/whilein/gitlab-pipeline-cleaner">
  </a>

  <a href="https://discord.gg/ANEHruraCc">
    <img src="https://img.shields.io/discord/819859288049844224?logo=discord">
  </a>

  <a href="https://github.com/whilein/gitlab-pipeline-cleaner/issues">
    <img src="https://img.shields.io/github/issues/whilein/gitlab-pipeline-cleaner">
  </a>

  <a href="https://github.com/whilein/gitlab-pipeline-cleaner/pulls">
    <img src="https://img.shields.io/github/issues-pr/whilein/gitlab-pipeline-cleaner">
  </a>
  <a href="https://hub.docker.com/r/whilein/gitlab-pipeline-cleaner">
    <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/whilein/gitlab-pipeline-cleaner" />
  </a>
</div>

## Configuration

## `url`

GitLab instance URL, i.e. `https://gitlab.com` or `http://localhost`

## `token`

Private Token for GitLab
API ([which tokens have API access?](https://docs.gitlab.com/ee/security/token_overview.html#available-scopes))

## `options`

Global options for all targets

Values:

- `keep_last` - Keep at least some amount of pipelines
- `delete_older_than` - Delete a pipelines older than some duration, for example `30d`
- `skip_statuses` - Skip a pipelines with specified statuses

## `targets`

List of projects or groups to search for a pipelines

## `targets:project` / `targets:project:name`

Project name

## `targets:group` / `targets:group:name`

Group name

### `targets:group:recursive`

Enable search in subgroups

### `targets:group:options`

Optional overrides of global options

### `targets:group:archive_inclusion`

Policy for archived projects

- `include` - include archived projects (default)
- `exclude` - exclude archived projects
- `only` - only archived projects

### `targets:group:exclude`

Exclude specified projects from searching (full path, i.e. `mygroup/myprojecttoexclude`)

## Environment

## `CONFIG_PATH`
Path to config file, by default `config.yml`.

## Deploy

### Docker

```bash
docker run --rm \
    -v './configuration:/configuration' \
    -e 'CONFIG_PATH=/configuration/config.yml' \
    whilein/gitlab-pipeline-cleaner
```

# TODO

- Child pipelines
- Merge Requests