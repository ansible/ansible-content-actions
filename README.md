# ansible-github-action

test.yaml

```
---
name: "CI"

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

on:  # yamllint disable-line rule:truthy
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
    uses: ansible/ansible-github-actions/.github/workflows/lint.yaml@main
  sanity:
    uses: ansible/ansible-github-actions/.github/workflows/sanity.yaml@main
  unit-galaxy:
    uses: ansible/ansible-github-actions/.github/workflows/unit.yaml@main
  all_green:
    if: ${{ always() }}
    needs:
      - changelog
      - sanity
      - unit-galaxy
      - ansible-lint
    runs-on: ubuntu-latest
    steps:
      - run: >-
          python -c "assert 'failure' not in
          set([
          '${{ needs.changelog.result }}',
          '${{ needs.sanity.result }}',
          '${{ needs.unit-galaxy.result }}'
          '${{ needs.ansible-lint.result }}'
          ])"

```

release.yaml

```
---
name: "Release collection"
on:  # yamllint disable-line rule:truthy
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

draft_release.yaml

```
---
name: "Draft release"
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
on:  # yamllint disable-line rule:truthy
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

check_label.yaml

```
---
name: "Check label"
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
on:  # yamllint disable-line rule:truthy
  pull_request_target:
    types: [opened, labeled, unlabeled, synchronize]
jobs:
  check_label:
    uses: ansible/ansible-github-actions/.github/workflows/check_label.yaml@main

```
