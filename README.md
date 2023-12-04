# ansible-github-action

test.yaml

```
---
name: CI

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

on:  # yamllint disable-line rule:truthy
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  changelog:
    uses: ansible/ansible-github-actions/.github/workflows/changelog.yaml@main
  ansible-lint:
    uses: ansible/ansible-github-actions/.github/workflows/lint.yaml@main
  sanity:
    uses: ansible/ansible-github-actions/.github/workflows/sanity.yaml@main
  unit:
    uses: ansible/ansible-github-actions/.github/workflows/unit.yaml@main
  integration:
    uses: ansible/ansible-github-actions/.github/workflows/integration.yaml@main

```

release.yaml

```
---
name: release
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
name: "Draft Release"
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
on:  # yamllint disable-line rule:truthy
  workflow_dispatch:
env:
  NAMESPACE: cisco
  COLLECTION_NAME: ios
  ANSIBLE_COLLECTIONS_PATHS: ./
jobs:
  update_release_draft:
    uses: ansible/ansible-github-actions/.github/workflows/draft_release.yaml@main
    with:
      repo: ansible-collections/cisco.ios
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
  ack:
    uses: ansible/ansible-github-actions/.github/workflows/check_label.yaml@main
```
