"""
Type stubs for gitpure - A pure git Python module implemented in Rust.
"""

from pathlib import Path
from typing import Type

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
