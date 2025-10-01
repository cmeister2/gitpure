import tempfile
from pathlib import Path

from git import Repo as GitPythonRepo

from gitpure import Repo

def test_clone_and_git_dir_worktree():
    """Test cloning a worktree repository and git_dir property"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = "https://github.com/cmeister2/gitpure"
        repo_path = Path(tmpdir) / "gitpure"
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

        # Metadata parity with GitPython
        gitpython_repo = GitPythonRepo(str(repo_path))

        gitpython_worktree = gitpython_repo.working_tree_dir
        assert gitpython_worktree is not None
        assert repo.working_tree_dir == Path(gitpython_worktree)
        assert repo.is_bare is False
        active_branch = repo.active_branch
        assert active_branch is not None
        assert active_branch.name == gitpython_repo.active_branch.name
        assert active_branch.commit is not None
        assert active_branch.commit.hexsha == gitpython_repo.active_branch.commit.hexsha

        head = repo.head
        assert head is not None
        assert head.commit is not None
        assert head.commit.hexsha == gitpython_repo.head.commit.hexsha
        gitpure_heads = repo.heads
        assert isinstance(gitpure_heads, list)
        assert all(hasattr(head, "name") and hasattr(head, "commit") for head in gitpure_heads)

        assert sorted(head.name for head in gitpure_heads) == sorted(
            head.name for head in gitpython_repo.heads
        )

        assert sorted(head.commit.hexsha for head in gitpure_heads if head.commit) == sorted(
            head.commit.hexsha for head in gitpython_repo.heads if head.commit
        )

        gitpure_tags = repo.tags
        assert isinstance(gitpure_tags, list)
        assert all(hasattr(tag, "name") and hasattr(tag, "commit") for tag in gitpure_tags)

        assert sorted(tag.name for tag in gitpure_tags) == sorted(
            tag.name for tag in gitpython_repo.tags
        )

        gitpure_tag_commits = {
            tag.name: (tag.commit.hexsha if tag.commit else None)
            for tag in gitpure_tags
        }
        gitpython_tag_commits = {
            tag.name: (tag.commit.hexsha if tag.commit else None)
            for tag in gitpython_repo.tags
        }
        assert gitpure_tag_commits == gitpython_tag_commits

def test_clone_and_git_dir_bare():
    """Test cloning a bare repository and git_dir property"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = "https://github.com/cmeister2/gitpure"
        repo_path = Path(tmpdir) / "gitpure.git"
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

        # Metadata parity with GitPython
        gitpython_repo = GitPythonRepo(str(repo_path))

        assert gitpython_repo.working_tree_dir is None
        assert repo.working_tree_dir is None
        assert repo.is_bare is True
        assert repo.active_branch is None

        head = repo.head
        assert head is not None
        assert head.commit is not None
        assert head.commit.hexsha == gitpython_repo.head.commit.hexsha
        gitpure_heads = repo.heads
        assert sorted(head.name for head in gitpure_heads) == sorted(
            head.name for head in gitpython_repo.heads
        )

        gitpure_tags = repo.tags
        assert sorted(tag.name for tag in gitpure_tags) == sorted(
            tag.name for tag in gitpython_repo.tags
        )

        gitpure_tag_commits = {
            tag.name: (tag.commit.hexsha if tag.commit else None)
            for tag in gitpure_tags
        }
        gitpython_tag_commits = {
            tag.name: (tag.commit.hexsha if tag.commit else None)
            for tag in gitpython_repo.tags
        }
        assert gitpure_tag_commits == gitpython_tag_commits


def test_branch_listing_matches_gitpython():
    """Ensure branch listings are aligned with GitPython."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = "https://github.com/cmeister2/gitpure"
        repo_path = Path(tmpdir) / "gitpure"
        repo = Repo.clone_from(repo_url, str(repo_path))

        gitpure_branches = repo.branches
        assert isinstance(gitpure_branches, list)
        assert all(hasattr(branch, "name") and hasattr(branch, "commit") for branch in gitpure_branches)

        gitpython_repo = GitPythonRepo(str(repo_path))
        gitpython_branches = sorted(head.name for head in gitpython_repo.branches)

        assert [branch.name for branch in gitpure_branches] == gitpython_branches

        # branches property should mirror heads property
        gitpure_heads = repo.heads
        assert [head.name for head in gitpure_heads] == [branch.name for branch in gitpure_branches]
