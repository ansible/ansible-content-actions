# ansible-content-actions

Combine GitHub Actions to create a streamlined workflow for testing Ansible collection repositories on GitHub.

## Usage

To use the action, create a workflow in your repository like
`.github/workflows/test.yaml`:

```yaml
---
name: ci

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

on:
  pull_request:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: "0 0 * * *"

jobs:
  changelog:
    uses: ansible/ansible-content-actions/.github/workflows/changelog.yaml@main
    if: github.event_name == 'pull_request'
  ansible-lint:
    uses: ansible/ansible-content-actions/.github/workflows/ansible_lint.yaml@main
  sanity:
    uses: ansible/ansible-content-actions/.github/workflows/sanity.yaml@main
  unit-galaxy:
    uses: ansible/ansible-content-actions/.github/workflows/unit.yaml@main
  integration:
    uses: ansible/ansible-content-actions/.github/workflows/integration.yaml@main
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
          '${{ needs.unit-galaxy.result }}'
          '${{ needs.ansible-lint.result }}'
          ])"
```

## Scope

This combined GitHub Action covers the following action workflows:

- Ansible-lint - Checks playbooks for practices and behavior that could potentially be improved.
- Sanity - Uses tox-ansible generates a testing matrix and runs sanity checks.
- Unit - Installs the collection and all its dependencies from Galaxy and runs unit tests against a matrix generated via tox-ansible.
- Integration - Installs the collection and all its dependencies from Galaxy and runs integration tests against a matrix generated via tox-ansible.
- Changelog - Checks for a changelog entry with the PR, fails if missing or invalid.
- Release - Push release to Automation Hub and Ansible Galaxy, requires (token/secrets).
- Release Galaxy - Push a release to Ansible Galaxy only.
- Release Automation Hub - Push a release to Ansible Automation Hub only.
- Draft Release - Generates changelog entries for release, also raises a PR with changelog and galaxy file updated.
- Check Label - Check if a valid label added to the PR is required by the release drafter.

## Licensing

ansible-content-actions is released under the Apache License version 2.

See the [LICENSE](https://github.com/ansible/ansible-content-actions/blob/main/LICENSE) file for more details.
