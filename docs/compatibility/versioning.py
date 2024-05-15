"""
This module provides a CLI to check if a version tag has the expected format we expect in the BO4E repository.
"""

import functools
import logging
import re
import subprocess
import sys
from typing import ClassVar, Iterable, Literal, Optional

import click
from bost.pull import get_source_repo
from github import Github
from github.Auth import Token
from github.GitRelease import GitRelease
from more_itertools import one
from pydantic import BaseModel, ConfigDict

from .__main__ import compare_bo4e_versions

logger = logging.getLogger(__name__)


@functools.total_ordering
class Version(BaseModel):
    """
    A class to represent a BO4E version number.
    """

    version_pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^v(?P<major>\d{6})\.(?P<functional>\d+)\.(?P<technical>\d+)(?:-rc(?P<candidate>\d+))?$"
    )

    major: int
    functional: int
    technical: int
    candidate: Optional[int] = None
    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_string(cls, version: str, allow_candidate: bool = False) -> "Version":
        """
        Parse a version string and return a Version object.
        Raises a ValueError if the version string does not match the expected pattern.
        Raises a ValueError if allow_candidate is False and the version string contains a candidate version.
        """
        match = cls.version_pattern.fullmatch(version)
        if match is None:
            raise ValueError(f"Expected version to match {cls.version_pattern}, got {version}")
        inst = cls(
            major=int(match.group("major")),
            functional=int(match.group("functional")),
            technical=int(match.group("technical")),
            candidate=int(match.group("candidate")) if match.group("candidate") is not None else None,
        )
        if not allow_candidate and inst.is_candidate():
            raise ValueError(f"Expected a version without candidate, got a candidate version: {version}")
        return inst

    @property
    def tag_name(self) -> str:
        """
        Return the tag name for this version.
        """
        return f"v{self.major}.{self.functional}.{self.technical}" + (
            f"-rc{self.candidate}" if self.is_candidate() else ""
        )

    def is_candidate(self) -> bool:
        """
        Return True if this version is a candidate version.
        """
        return self.candidate is not None

    def bumped_major(self, other: "Version") -> bool:
        """
        Return True if this version is a major bump from the other version.
        """
        return self.major > other.major

    def bumped_functional(self, other: "Version") -> bool:
        """
        Return True if this version is a functional bump from the other version.
        Return False if major bump is detected.
        """
        return not self.bumped_major(other) and self.functional > other.functional

    def bumped_technical(self, other: "Version") -> bool:
        """
        Return True if this version is a technical bump from the other version.
        Return False if major or functional bump is detected.
        """
        return not self.bumped_functional(other) and self.technical > other.technical

    def bumped_candidate(self, other: "Version") -> bool:
        """
        Return True if this version is a candidate bump from the other version.
        Return False if major, functional or technical bump is detected.
        Raises ValueError if one of the versions is not a candidate version.
        """
        if self.candidate is not None or other.candidate is not None:
            raise ValueError("Cannot compare candidate versions if one of them is not a candidate.")
        return not self.bumped_technical(other) and self.candidate > other.candidate

    def __gt__(self, other: "Version"):
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self.major > other.major
            or self.functional > other.functional
            or self.technical > other.technical
            or (self.is_candidate() and (not other.is_candidate() or self.candidate > other.candidate))
        )

    def __eq__(self, other: "Version"):
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self.major == other.major
            and self.functional == other.functional
            and self.technical == other.technical
            and self.is_candidate() == other.is_candidate()
            and (not self.is_candidate() or self.candidate == other.candidate)
        )

    def __str__(self):
        return self.tag_name


def get_latest_version(gh_token: str | None = None) -> Version:
    """
    Get the release from BO4E-python repository which is marked as 'latest'.
    """
    if gh_token is not None:
        gh = Github(auth=Token(gh_token))
    else:
        gh = Github()
    return Version.from_string(gh.get_repo("bo4e/BO4E-python").get_latest_release().tag_name)


def get_last_n_tags(n: int, *, on_branch: str = "main", exclude_candidates: bool = True) -> Iterable[str]:
    """
    Get the last n tags from the repository.
    """
    try:
        Version.from_string(on_branch, allow_candidate=True)
    except ValueError:
        reference = f"remotes/origin/{on_branch}"
    else:
        reference = f"tags/{on_branch}"
    output = subprocess.check_output(["git", "tag", "--merged", reference, "--sort=-creatordate"]).decode().splitlines()
    if reference.startswith("tags/"):
        output = output[1:]  # Skip the reference tag

    counter = 0
    for tag in output:
        if counter >= n:
            return
        version = Version.from_string(tag, allow_candidate=True)
        if exclude_candidates and version.is_candidate():
            continue
        yield tag
        counter += 1
    if counter < n:
        if reference.startswith("tags/"):
            logger.warning("Only found %d tags before tag %s, tried to retrieve %d", counter, on_branch, n)
        else:
            logger.warning("Only found %d tags on branch %s, tried to retrieve %d", counter, on_branch, n)


def get_last_version_before(version: Version) -> Version:
    """
    Get the last non-candidate version before the provided version following the commit history.
    """
    return Version.from_string(one(get_last_n_tags(1, on_branch=version.tag_name)))


def ensure_latest_on_main(latest_version: Version, is_cur_version_latest: bool):
    """
    Ensure that the latest release is on the main branch.
    Will also be called if the currently tagged version is marked as `latest`.
    In this case both versions are equal.

    Note: This doesn't revert the release on GitHub. If you accidentally released on the wrong branch, you have to
    manually mark an old or create a new release as `latest` on the main branch. Otherwise, the publish workflow
    will fail here.
    """
    commit_id = subprocess.check_output(["git", "rev-parse", f"tags/{latest_version.tag_name}~0"]).decode().strip()
    output = subprocess.check_output(["git", "branch", "-a", "--contains", f"{commit_id}"]).decode()
    branches_containing_commit = [line.strip().lstrip("*").lstrip() for line in output.splitlines()]
    if "remotes/origin/main" not in branches_containing_commit:
        if is_cur_version_latest:
            raise ValueError(
                f"Tagged version {latest_version} is marked as latest but is not on main branch "
                f"(branches {branches_containing_commit} contain commit {commit_id}).\n"
                "Either tag on main branch or don't mark the release as latest.\n"
                "If you accidentally marked the release as latest please remember to revert it. "
                "Otherwise, the next publish workflow will fail as the latest version is assumed to be on main.\n"
                f"Output from git-command: {output}"
            )
        raise ValueError(
            f"Fatal Error: Latest release {latest_version.tag_name} is not on main branch "
            f"(branches {branches_containing_commit} contain commit {commit_id}).\n"
            "Please ensure that the latest release is on the main branch.\n"
            f"Output from git-command: {output}"
        )


def compare_work_tree_with_latest_version(
    gh_version: str, gh_token: str | None = None, major_bump_allowed: bool = True
):
    """
    Compare the work tree with the latest release from the BO4E repository.
    """
    logger.info("Github Access Token %s", "provided" if gh_token is not None else "not provided")
    cur_version = Version.from_string(gh_version, allow_candidate=True)
    logger.info("Tagged release version: %s", cur_version)
    latest_version = get_latest_version(gh_token)
    logger.info("Got latest release version from GitHub: %s", latest_version)
    is_cur_version_latest = cur_version == latest_version
    if is_cur_version_latest:
        logger.info("Tagged version is marked as latest.")
    ensure_latest_on_main(latest_version, is_cur_version_latest)
    logger.info("Latest release is on main branch.")

    version_ahead = cur_version
    version_behind = get_last_version_before(cur_version)
    logger.info(
        "Comparing with the version before the tagged release (excluding release candidates): %s",
        version_behind,
    )

    assert version_ahead > version_behind, f"Version did not increase: {version_ahead} <= {version_behind}"

    logger.info(
        "Current version is ahead of the compared version. Comparing versions: %s -> %s",
        version_behind,
        version_ahead,
    )
    if version_ahead.bumped_major(version_behind):
        if not major_bump_allowed:
            raise ValueError("Major bump detected. Major bump is not allowed.")
        logger.info("Major version bump detected. No further checks needed.")
        return
    changes = list(
        compare_bo4e_versions(version_behind.tag_name, version_ahead.tag_name, gh_token=gh_token, from_local=True)
    )
    logger.info("Check if functional or technical release bump is needed")
    functional_changes = len(changes) > 0
    logger.info("%s release bump is needed", "Functional" if functional_changes else "Technical")

    if not functional_changes and version_ahead.bumped_functional(version_behind):
        raise ValueError(
            "Functional version bump detected but no functional changes found. "
            "Please bump the technical release count instead of the functional."
        )
    if functional_changes and not version_ahead.bumped_functional(version_behind):
        raise ValueError(
            "No functional version bump detected but functional changes found. "
            "Please bump the functional release count.\n"
            f"Detected changes: {changes}"
        )


@click.command()
@click.option("--gh-version", type=str, required=True, help="The new version to compare the latest release with.")
@click.option(
    "--gh-token", type=str, default=None, help="GitHub Access token. This helps to avoid rate limiting errors."
)
@click.option(
    "--major-bump-allowed/--major-bump-disallowed",
    is_flag=True,
    default=True,
    help="Indicate if a major bump is allowed. "
    "If it is not allowed, the script will exit with an error if a major bump is detected.",
)
def compare_work_tree_with_latest_version_cli(
    gh_version: str, gh_token: str | None = None, major_bump_allowed: bool = True
):
    """
    Check a version tag and compare the work tree with the latest release from the BO4E repository.
    Exits with status code 1 iff the version is inconsistent with the commit history or if the detected changes in
    the JSON-schemas are inconsistent with the version bump.
    """
    try:
        compare_work_tree_with_latest_version(gh_version, gh_token, major_bump_allowed)
    except Exception as error:
        logger.error("An error occurred.", exc_info=error)
        raise click.exceptions.Exit(1)
    logger.info("All checks passed.")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    compare_work_tree_with_latest_version_cli()


def test_compare_work_tree_with_latest_version():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    compare_work_tree_with_latest_version("v202401.1.2-rc3", gh_token=None)
