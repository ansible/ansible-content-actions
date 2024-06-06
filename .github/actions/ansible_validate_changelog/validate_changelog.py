#!/usr/bin/python
"""Script to check if a PR has a correct changelog fragment."""

import argparse
import logging
import re
import subprocess
import sys

from collections import defaultdict
from pathlib import Path

import yaml


FORMAT = "[%(asctime)s] - %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("validate_changelog")
logger.setLevel(logging.DEBUG)


def is_changelog_file(ref: str) -> bool:
    """Check if a file is a changelog fragment.

    :param ref: the file to be checked
    :returns: True if file is a changelog fragment else False
    """
    match = re.match(r"^changelogs/fragments/(.*)\.(yaml|yml)$", ref)
    return bool(match)


def is_module_or_plugin(ref: str) -> bool:
    """Check if a file is a module or plugin.

    :param ref: the file to be checked
    :returns: True if file is a module or plugin else False
    """
    prefix_list = (
        "plugins/modules",
        "plugins/module_utils",
        "plugins/action",
        "plugins/inventory",
        "plugins/lookup",
        "plugins/filter",
        "plugins/connection",
        "plugins/become",
        "plugins/cache",
        "plugins/callback",
        "plugins/cliconf",
        "plugins/httpapi",
        "plugins/netconf",
        "plugins/shell",
        "plugins/strategy",
        "plugins/terminal",
        "plugins/test",
        "plugins/vars",
        "roles/",
        "playbooks/",
        "meta/runtime.yml",
    )
    return ref.startswith(prefix_list)


def is_documentation_file(ref: str) -> bool:
    """Check if a file is a documentation file.

    :param ref: the file to be checked
    :returns: True if file is a documentation file else False
    """
    prefix_list = (
        "docs/",
        "plugins/doc_fragments",
    )
    return ref.startswith(prefix_list)


def is_release_pr(changes: dict[str, list[str]]) -> bool:
    """Determine whether the changeset looks like a release.

    :param changes: A dictionary keyed on change status (A, M, D, etc.) of lists of changed files
    :returns: True if the changes match a collection release else False
    """
    # Should only have Deleted and Modified files.
    if not set(changes.keys()).issubset(("D", "M")):
        return False

    # All deletions should be of changelog files
    if not all(is_changelog_file(x) for x in changes["D"]):
        return False

    # A collection release should only change these files
    if not set(changes["M"]).issubset(
        ("CHANGELOG.rst", "changelogs/changelog.yaml", "galaxy.yml")
    ):
        return False

    return True


def is_changelog_needed(changes: dict[str, list[str]]) -> bool:
    """Determine whether a changelog fragment is necessary.

    :param changes: A dictionary keyed on change status (A, M, D, etc.) of lists of changed files
    :returns: True if a changelog fragment is not required for this PR else False
    """
    # Changes to existing plugins or modules require a changelog
    # Changelog entries are not needed for new plugins or modules
    # https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#generating-changelogs
    modifications = changes["M"] + changes["D"]
    if any(is_module_or_plugin(x) for x in modifications):
        return True

    return False


def is_valid_changelog_format(path: str) -> bool:
    """Check if changelog fragment is formatted properly.

    :param path: the file to be checked
    :returns: True if the file passes validation else False
    """
    try:
        config = Path("changelogs/config.yaml")
        with open(config, "rb") as config_file:
            changelog_config = yaml.safe_load(config_file)
            changes_type = tuple(item[0] for item in changelog_config["sections"])
            changes_type += (changelog_config["trivial_section_name"],)
            changes_type += (changelog_config["prelude_section_name"],)
            logger.info("Found the following changelog sections: %s", changes_type)
    except (OSError, yaml.YAMLError) as exc:
        logger.info(
            "Failed to read changelog config, using default sections instead: %s", exc
        )
        # https://github.com/ansible-community/antsibull-changelog/blob/main/docs/changelogs.rst#changelog-fragment-categories
        changes_type = (
            "release_summary",
            "breaking_changes",
            "major_changes",
            "minor_changes",
            "removed_features",
            "deprecated_features",
            "security_fixes",
            "bugfixes",
            "known_issues",
            "trivial",
        )

    try:
        with open(path, "rb") as file_desc:
            result = list(yaml.safe_load_all(file_desc))

        for section in result:
            for key in section.keys():
                if key not in changes_type:
                    msg = f"{key} from {path} is not a valid changelog type"
                    logger.error(msg)
                    return False
                if key == "release_summary" and not isinstance(section[key], str):
                    logger.error("release_summary should not be a list")
                    return False
                elif key != "release_summary" and not isinstance(section[key], list):
                    logger.error(
                        "Changelog section %s from file %s must be a list, '%s' found instead.",
                        key,
                        path,
                        type(section[key]),
                    )
                    return False
        return True
    except (OSError, yaml.YAMLError) as exc:
        msg = f"yaml loading error for file {path} -> {exc}"
        logger.error(msg)
        return False


def run_command(cmd: str) -> tuple[int, str, str]:
    """Run a command and return the response.

    :param cmd: The command to run
    :returns: A tuple of (return code, stdout, stderr)
    """
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        encoding="utf-8",
    ) as proc:
        out, err = proc.communicate()
        return proc.returncode, out, err


def list_files(ref: str) -> dict[str, list[str]]:
    """List all files changed since ref, grouped by change status.

    :param ref: The git ref to compare to
    :returns: A dictionary keyed on change status (A, M, D, etc.) of lists of changed files
    :raises ValueError: If the file gathering command fails
    """
    command = "git diff origin/" + ref + " --name-status"
    logger.info("Executing -> %s", command)
    ret_code, stdout, stderr = run_command(command)
    if ret_code != 0:
        raise ValueError(stderr)

    changes: dict[str, list[str]] = defaultdict(list)
    for file in stdout.split("\n"):
        file_attr = file.split("\t")
        if len(file_attr) == 2:
            changes[file_attr[0]].append(file_attr[1])
    logger.info("changes -> %s", changes)
    return changes


def main(ref: str) -> None:
    """Run the script.

    :param ref: The pull request base ref
    """
    changes = list_files(ref)
    if changes:
        if is_release_pr(changes):
            logger.info("This PR looks like a release!")
            sys.exit(0)

        changelog = [x for x in changes["A"] if is_changelog_file(x)]
        logger.info("changelog files -> %s", changelog)
        if not changelog:
            if is_changelog_needed(changes):
                logger.error(
                    "Missing changelog fragment. This is not required"
                    " only if PR adds new modules and plugins or contain"
                    " only documentation changes."
                )
                sys.exit(1)
            logger.info(
                "Changelog not required as PR adds new modules and/or"
                " plugins or contain only documentation changes."
            )
        else:
            invalid_changelog_files = [
                x for x in changelog if not is_valid_changelog_format(x)
            ]
            if invalid_changelog_files:
                logger.error(
                    "The following changelog files are not valid -> %s",
                    invalid_changelog_files,
                )
                sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate changelog file from new commit"
    )
    parser.add_argument("--ref", required=True, help="Pull request base ref")

    args = parser.parse_args()
    main(args.ref)
