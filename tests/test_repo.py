import tempfile
from pathlib import Path

from gitpure import Repo 

def test_clone_and_git_dir_worktree():
    """Test cloning a worktree repository and git_dir property"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = "https://github.com/curl/wcurl"
        repo_path = Path(tmpdir) / "wcurl"
        repo = Repo.clone_from(repo_url, str(repo_path))
        
        # Test basic clone functionality
        assert (repo_path / ".git").exists()
        assert (repo_path / "README.md").exists()
        
        # Test git_dir property
        git_dir = repo.git_dir
        expected_git_dir = repo_path / ".git"
        
        # Should return the correct path
        assert Path(git_dir) == expected_git_dir
        
        # The returned path should exist and be a directory
        assert Path(git_dir).exists()
        assert Path(git_dir).is_dir()
        
        # Should contain typical git directory contents
        git_dir_path = Path(git_dir)
        assert (git_dir_path / "HEAD").exists()
        assert (git_dir_path / "config").exists()
        assert (git_dir_path / "objects").exists()
        assert (git_dir_path / "refs").exists()
        
        # Test git_dir property type and consistency
        assert isinstance(git_dir, Path)
        assert git_dir.is_absolute()
        
        # Multiple calls should return the same result
        git_dir2 = repo.git_dir
        git_dir3 = repo.git_dir
        assert git_dir == git_dir2 == git_dir3

def test_clone_and_git_dir_bare():
    """Test cloning a bare repository and git_dir property"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = "https://github.com/curl/wcurl"
        repo_path = Path(tmpdir) / "wcurl.git"
        repo = Repo.clone_from(repo_url, str(repo_path), bare=True)
        
        # Test bare clone functionality
        # Should NOT have .git subdirectory (it IS the git directory)
        assert not (repo_path / ".git").exists()
        
        # Should have git files directly in the root
        assert (repo_path / "HEAD").exists()
        assert (repo_path / "config").exists()
        assert (repo_path / "objects").exists()
        assert (repo_path / "refs").exists()
        
        # Should NOT have working tree files
        assert not (repo_path / "README.md").exists()
        
        # Test git_dir property for bare repo
        git_dir = repo.git_dir
        
        # For bare repos, git_dir should be the repo directory itself
        assert Path(git_dir) == repo_path
        
        # The returned path should exist and be a directory
        assert Path(git_dir).exists()
        assert Path(git_dir).is_dir()
        
        # Test git_dir property type
        assert isinstance(git_dir, Path)
        assert git_dir.is_absolute()
