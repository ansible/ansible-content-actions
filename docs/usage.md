# Using

## The CI workflow

This guide shows how to use various GitHub actions available.
The following GitHub actions are to be added under `.github/workflows` directory as `{filename}.yaml`

This GitHub Actions workflow automates various tasks related to Ansible development, including changelog generation, linting, integration, sanity checks, and unit tests. The `all_green` job ensures that all the previous tasks passed successfully.

Filename: `test.yaml`

```
---
name: "CI"

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

on:
  pull_request:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'

jobs:
  changelog:
    uses: ansible/ansible-github-actions/.github/workflows/changelog.yaml@main
    if: github.event_name == 'pull_request'
  ansible-lint:
    uses: ansible/ansible-github-actions/.github/workflows/ansible_lint.yaml@main
  sanity:
    uses: ansible/ansible-github-actions/.github/workflows/sanity.yaml@main
  unit-galaxy:
    uses: ansible/ansible-github-actions/.github/workflows/unit.yaml@main
  integration:
    uses: ansible/ansible-github-actions/.github/workflows/integration.yaml@main
  all_green:
    if: ${{ always() }}
    needs:
      - changelog
      - sanity
      - integration
      - unit-galaxy
      - ansible-lint
    runs-on: ubuntu-latest
    steps:
      - run: >-
          python -c "assert 'failure' not in
          set([
          '${{ needs.changelog.result }}',
          '${{ needs.integration.result }}',
          '${{ needs.sanity.result }}',
          '${{ needs.unit-galaxy.result }}',
          '${{ needs.ansible-lint.result }}'
          ])"
```

## The release workflow

This GitHub action releases the collection in Ansible Automation Hub and Ansible Galaxy, it is dependent on the environment `release` which must contain the following secrets.

`AH_TOKEN`: The Automation Hub token required for to interact with Ansible Automation Hub.
`ANSIBLE_GALAXY_API_KEY`: A Galaxy token required to interact with Ansible Galaxy.

Note - ansible-github-actions/release.yaml uses release_ah.yaml and release_galaxy.yaml internally.

Filename: `release.yaml`

```
---
name: "Release collection"
on:
  release:
    types: [published]

jobs:
  release:
    uses: ansible/ansible-github-actions/.github/workflows/release.yaml@main
    with:
      environment: release
    secrets:
      ah_token: ${{ secrets.AH_TOKEN }}
      ansible_galaxy_api_key: ${{ secrets.ANSIBLE_GALAXY_API_KEY }}
```

## The check label workflow (previously ack)

This GitHub action checks, if a valid label added to the PR. It fails if a valid label is missing.

Filename: check_label.yaml

```
---
name: "Check label"
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
on:
  pull_request_target:
    types: [opened, labeled, unlabeled, synchronize]
jobs:
  check_label:
    uses: ansible/ansible-github-actions/.github/workflows/check_label.yaml@main
```

## The release drafter workflow (previously push)

This GitHub action is dependent on `check_label` workflow, and the environment `push`, which must contain a secret `BOT_PAT` that must be a GitHub token, to enable the bot/user to add a changelog PR to the desired repo.
The workflow runs antsibull-changelog, ansichaut, pre-commit, updates version in galaxy.yml file and creates a PR with the changelog updates.
Also, this runs release-drafter which is essential for a draft release entry in GitHub UI, considering PRs that got merge fragmenting on basis of the labels added to individual PR. Refer to `release-drafter.yml` for more information.

Filename: `draft_release.yaml`

```
---
name: "Draft release"
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
on:
  workflow_dispatch:
env:
  NAMESPACE: ${{ github.repository_owner }}
  COLLECTION_NAME: utils
  ANSIBLE_COLLECTIONS_PATHS: ./
jobs:
  update_release_draft:
    uses: ansible/ansible-github-actions/.github/workflows/draft_release.yaml@main
    with:
      repo: ${{ github.event.pull_request.head.repo.full_name }}
    secrets:
      BOT_PAT: ${{ secrets.BOT_PAT }}
```

## The Automation Hub token refresh workflow

This workflow, is supposed to run in a schedule (once daily), this checks and refreshes automation hub token. The workflow is dependent on the environment `release` which must contain the following secrets.

`AH_TOKEN`: The Automation Hub token required for to interact with Ansible Automation Hub.

Filename: `refresh_ah_token.yaml`

```
---
name: "Refresh Automation Hub token"
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  refresh:
    uses: ansible/ansible-github-actions/.github/workflows/refresh_ah_token.yaml@main
    with:
      environment: release
    secrets:
      ah_token: ${{ secrets.AH_TOKEN }}
```

## Dependencies and requirements

The GitHub action uses tox-ansible which requires a tox-ansible.ini, a default tox-ansible.ini is pushed with a default skip list, and the task is skipped if the collection contains it.

- [`requirements.yml`](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html#installing-roles-and-collections-from-the-same-requirements-yml-file)
- `roles/requirements.yml`
- `collections/requirements.yml`
- `tests/requirements.yml`
- `tests/integration/requirements.yml`
- `tests/unit/requirements.yml`
- [`galaxy.yml`](https://docs.ansible.com/ansible/latest/dev_guide/collections_galaxy_meta.html)
