# ansible-content-action

holds all the GHA just to reference
be wise

Make sure to disable all API push to sensitive places

```
---
name: test_mono

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

on:  # yamllint disable-line rule:truthy
  pull_request:
    branches: [main]
  workflow_dispatch:
  # schedule:
  #   - cron: "0 0 * * *"

jobs:
  ansible-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: ansible-network/github_actions/.github/actions/checkout_dependency@main

      - name: Run ansible-lint
        uses: KB-perByte/ansible-content-action@main

  sanity:
    env:
      PY_COLORS: "1"
      source_directory: "./source"
    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu-latest
        ansible-version:
          - stable-2.9
          - stable-2.13
          - stable-2.14
          - stable-2.15
          - milestone
          - devel
        python-version:
          - "3.7"
          - "3.8"
          - "3.9"
          - "3.10"
          - "3.11"
        exclude:
          - ansible-version: "stable-2.9"
            python-version: '3.9'
          - ansible-version: "stable-2.9"
            python-version: '3.10'
          - ansible-version: "stable-2.9"
            python-version: '3.11'
          - ansible-version: "stable-2.13"
            python-version: '3.7'
          - ansible-version: "stable-2.13"
            python-version: '3.11'
          - ansible-version: "stable-2.14"
            python-version: '3.7'
          - ansible-version: "stable-2.14"
            python-version: '3.8'
          - ansible-version: "stable-2.15"
            python-version: '3.7'
          - ansible-version: "stable-2.15"
            python-version: '3.8'
          - ansible-version: "milestone"
            python-version: '3.7'
          - ansible-version: "milestone"
            python-version: '3.8'
          - ansible-version: "milestone"
            python-version: '3.9'
          - ansible-version: "devel"
            python-version: '3.7'
          - ansible-version: "devel"
            python-version: '3.8'
          - ansible-version: "devel"
            python-version: '3.9'
        include:
          - ansible-version: "stable-2.9"
            python-version: '3.6'
            os: "ubuntu-20.04"
        unstable:
          - "devel"
    runs-on: ${{ matrix.os }}
    continue-on-error: ${{ contains(matrix.unstable, matrix.ansible-version) }}
    steps:
      - uses: ansible-network/github_actions/.github/actions/checkout_dependency@main

      - name: "py${{ matrix.python-version }} / ${{ matrix.os }} / ${{ matrix.ansible-version }}"
        uses: KB-perByte/ansible-content-action@main
```

Strictly, WIP
