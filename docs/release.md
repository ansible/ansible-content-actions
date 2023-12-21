# Using

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

The workflow run results in

![Alt text](./docs/images/release.png?raw=true "Release collection")

The release works in two parts, Automation hub release and then Ansible Galaxy release. If the Automation hub release fails, the Galaxy job is skipped.
