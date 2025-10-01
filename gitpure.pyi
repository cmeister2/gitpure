"""
Type stubs for gitpure - A pure git Python module implemented in Rust.
"""

from pathlib import Path
from typing import Type


class Commit:
    """Lightweight representation of a git commit."""

    @property
    def hexsha(self) -> str:
        """Hexadecimal object id of the commit."""
        ...


class Head:
    """A named reference to a commit, mirroring GitPython's Head."""

    @property
    def name(self) -> str:
        """The short name of the head (branch)."""
        ...

    @property
    def commit(self) -> Commit | None:
        """The commit the head points to, if available."""
        ...


class Tag:
    """A tag reference with optional peeled commit."""

    @property
    def name(self) -> str:
        """The short name of the tag."""
        ...

    @property
    def commit(self) -> Commit | None:
        """The commit the tag ultimately refers to, if available."""
        ...

class Repo:
    """A git repository wrapper using gix (gitoxide)."""

    @property
    def git_dir(self) -> Path:
        """
        Path to the .git directory of the repository.

        Returns:
            The absolute path to the .git directory as a pathlib.Path object
        """
        ...

    def branches(self) -> list[str]:
        """Return the names of all local branches in the repository."""
        ...

    @property
    def working_tree_dir(self) -> Path | None:
        """Return the working tree directory of the repository, if it exists."""
        ...

    @property
    def is_bare(self) -> bool:
        """Whether the repository is bare (has no working tree)."""
        ...

    @property
    def active_branch(self) -> Head | None:
        """Current active branch as a Head object, if available."""
        ...

    @property
    def head(self) -> Head | None:
        """HEAD reference as a Head object, if available."""
        ...

    @property
    def heads(self) -> list[Head]:
        """Return all local heads (branches) in the repository."""
        ...

    @property
    def tags(self) -> list[Tag]:
        """Return all tags in the repository."""
        ...

    @classmethod
    def clone_from(cls: Type["Repo"], url: str, to_path: str, bare: bool = False) -> "Repo":
        """
        Clone a repository from a URL to a local path.

        Args:
            url: The URL of the repository to clone
            to_path: The local path where the repository should be cloned
            bare: Whether to create a bare repository (default: False)

        Returns:
            A new Repo instance representing the cloned repository

        Raises:
            RuntimeError: If the clone operation fails
        """
        ...
