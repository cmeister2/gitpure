# gitpure

[![CI](https://github.com/cmeister2/gitpure/actions/workflows/CI.yml/badge.svg)](https://github.com/cmeister2/gitpure/actions/workflows/CI.yml)
[![PyPI version](https://badge.fury.io/py/gitpure.svg)](https://badge.fury.io/py/gitpure)
[![Python versions](https://img.shields.io/pypi/pyversions/gitpure.svg)](https://pypi.org/project/gitpure/)

A pure git Python library implemented in Rust using [gitoxide](https://github.com/Byron/gitoxide). This library provides fast and memory-efficient git operations through Python bindings.

## Features

- **Fast**: Built with Rust and gitoxide for optimal performance
- **Memory efficient**: Leverages Rust's memory management
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Pure Python interface**: Easy to use Python API
- **Safe**: Thread-safe operations with Rust's ownership model

## Installation

Install from PyPI:

```bash
pip install gitpure
```

## Quick Start

```python
import gitpure

# Clone a repository (with worktree)
repo = gitpure.Repo.clone_from("https://github.com/user/repo.git", "/path/to/local/repo")

# Clone a bare repository
bare_repo = gitpure.Repo.clone_from("https://github.com/user/repo.git", "/path/to/bare/repo", bare=True)

# Get the git directory path
git_dir = repo.git_dir
print(f"Git directory: {git_dir}")
```

## Development

### Prerequisites

- Python 3.8+
- Rust 1.70+
- maturin

### Building from Source

```bash
# Clone the repository
git clone https://github.com/cmeister2/gitpure.git
cd gitpure

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install maturin
pip install maturin

# Build and install in development mode
maturin develop

# Or build wheel
maturin build --release
```

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## Release process

Releases are fully automated with [semantic-release](https://semantic-release.gitbook.io/). The pipeline will:

1. Inspect the commit history on `main` using Conventional Commits to determine the next semantic version.
2. Prepare the Rust crate via `semantic-release-cargo`, ensuring `Cargo.toml` and the Python wheel share the same version.
3. Build wheels and source distributions with `maturin` and attach them to the GitHub release.
4. Publish the distribution artifacts to PyPI.

To keep releases working you must:

- Continue to write commits that follow the Conventional Commits specification (`feat:`, `fix:`, etc.).

You can trigger a release by merging changes into `main`.

## Architecture

gitpure is built on top of:

- **[gitoxide](https://github.com/Byron/gitoxide)**: A pure Rust implementation of git
- **[PyO3](https://github.com/PyO3/pyo3)**: Python bindings for Rust
- **[maturin](https://github.com/PyO3/maturin)**: Build tool for Python extensions written in Rust

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
