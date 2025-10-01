use gix::bstr::ByteSlice;
use gix::Id;
use pyo3::exceptions::{PyRuntimeError, PyTypeError};
use pyo3::{prelude::*, types::PyType};
use std::collections::BTreeSet;
use std::path::Path;

#[pyclass]
#[derive(Hash, PartialEq, Eq, PartialOrd, Ord, Clone)]
struct Commit {
    hexsha: String,
}

#[pymethods]
impl Commit {
    #[getter]
    fn hexsha(&self) -> &str {
        &self.hexsha
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("<gitpure.Commit \"{}\">", self.hexsha))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.hexsha.clone())
    }
}

impl Commit {
    fn from_id(id_: Id) -> Self {
        Self {
            hexsha: id_.detach().to_string(),
        }
    }
}

#[pyclass]
#[derive(Hash, PartialEq, Eq, PartialOrd, Ord)]
struct Head {
    name: String,
    commit: Option<Commit>,
}

#[pymethods]
impl Head {
    #[getter]
    fn name(&self) -> &str {
        &self.name
    }

    #[getter]
    fn commit(&self) -> PyResult<Option<Commit>> {
        Ok(self.commit.clone())
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("<gitpure.Head \"{}\">", self.name))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.name.clone())
    }
}

impl Head {
    fn from_reference(reference: gix::Reference) -> Self {
        let mut reference = reference;
        let name = shorten_reference_name(&reference);
        let commit = reference
            .peel_to_id_in_place()
            .ok()
            .map(Commit::from_id);
        Self { name, commit }
    }
}

#[pyclass(module = "gitpure")]
#[derive(Hash, PartialEq, Eq, PartialOrd, Ord)]
struct Tag {
    name: String,
    commit: Option<Commit>,
}

#[pymethods]
impl Tag {
    #[getter]
    fn name(&self) -> &str {
        &self.name
    }

    #[getter]
    fn commit(&self) -> PyResult<Option<Commit>> {
        Ok(self.commit.clone())
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("<gitpure.Tag \"{}\">", self.name))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.name.clone())
    }
}

impl Tag {
    fn from_reference(reference: gix::Reference) -> Self {
        let mut reference = reference;
        let name = shorten_reference_name(&reference);
        let commit = reference
            .peel_to_id_in_place()
            .ok()
            .map(Commit::from_id);
        Self { name, commit }
    }
}

#[pyclass(unsendable)]
struct Repo {
    inner: gix::Repository,
}

fn path_to_python(py: Python<'_>, path: &Path) -> PyResult<Py<PyAny>> {
    let pathlib = py.import("pathlib")?;
    let path_class = pathlib.getattr("Path")?;
    Ok(path_class.call1((path.as_os_str(),))?.into())
}

fn shorten_reference_name(reference: &gix::Reference) -> String {
    let short_name = reference.name().shorten();
    match short_name.to_str() {
        Ok(valid) => valid.to_owned(),
        Err(_) => short_name.to_string(),
    }
}

#[pymethods]
impl Repo {
    /// The path to the `.git` directory of the repository.
    #[getter]
    fn git_dir(&self, py: Python) -> PyResult<Py<PyAny>> {
        path_to_python(py, self.inner.git_dir())
    }

    /// The path to the working tree directory, if present.
    #[getter]
    fn working_tree_dir(&self, py: Python) -> PyResult<Option<Py<PyAny>>> {
        match self.inner.workdir() {
            Some(path) => Ok(Some(path_to_python(py, path)?)),
            None => Ok(None),
        }
    }

    /// Returns true if the repository is bare.
    #[getter]
    fn is_bare(&self) -> bool {
        self.inner.workdir().is_none()
    }

    /// Clone a git repository from the given URL into the specified path.
    #[classmethod]
    #[pyo3(signature = (url, to_path, bare=false))]
    fn clone_from(
        _cls: &Bound<'_, PyType>,
        url: &str,
        to_path: &str,
        bare: bool,
    ) -> PyResult<Self> {
        let target_path = Path::new(to_path);

        // Configure the repository kind based on bare flag
        let kind = if bare {
            gix::create::Kind::Bare
        } else {
            gix::create::Kind::WithWorktree
        };

        let mut prepare_clone = gix::clone::PrepareFetch::new(
            url,
            target_path,
            kind,
            gix::create::Options::default(),
            gix::open::Options::isolated(),
        )
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to prepare clone: {}", e)))?;

        let (mut prepare_checkout, _outcome) = prepare_clone
            .fetch_then_checkout(gix::progress::Discard, &gix::interrupt::IS_INTERRUPTED)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to fetch repository: {}", e)))?;

        if bare {
            let repo = prepare_checkout.persist();
            Ok(Repo { inner: repo })
        } else {
            let (repo, _checkout_outcome) = prepare_checkout
                .main_worktree(gix::progress::Discard, &gix::interrupt::IS_INTERRUPTED)
                .map_err(|e| {
                    PyRuntimeError::new_err(format!("Failed to checkout worktree: {}", e))
                })?;

            Ok(Repo { inner: repo })
        }
    }

    /// Return all local branches in the repository.
    #[getter]
    fn branches(&self) -> PyResult<Vec<Head>> {
        self.heads()
    }

    /// Return the path to the current active branch, if any.
    #[getter]
    fn active_branch(&self) -> PyResult<Option<Head>> {
        if self.is_bare() {
            return Ok(None);
        }

        let head = self
            .inner
            .head()
            .map_err(|err| PyRuntimeError::new_err(format!("Failed to access HEAD: {err}")))?;

        // If HEAD is detached then raise a TypeError like GitPython does
        if head.is_detached() {
            return Err(PyTypeError::new_err(
                "HEAD is detached; no active branch".to_string(),
            ));
        }

        if head.is_unborn() {
            return Ok(None);
        }

        Ok(head.try_into_referent().map(Head::from_reference))
    }

    /// Return the commit id pointed to by HEAD, if available.
    #[getter]
    fn head(&self) -> PyResult<Option<Head>> {
        let head = self
            .inner
            .head()
            .map_err(|err| PyRuntimeError::new_err(format!("Failed to access HEAD: {err}")))?;

        Ok(head.try_into_referent().map(Head::from_reference))
    }

    /// List all local heads (branches) in the repository.
    #[getter]
    fn heads(&self) -> PyResult<Vec<Head>> {
        let platform = self.inner.references().map_err(|err| {
            PyRuntimeError::new_err(format!("Failed to access references: {err}"))
        })?;

        let iter = platform.local_branches().map_err(|err| {
            PyRuntimeError::new_err(format!("Failed to list local branches: {err}"))
        })?;

        let heads: BTreeSet<Head> = iter
            .map(|reference_result| {
                reference_result.map_err(|err| {
                    PyRuntimeError::new_err(format!(
                        "Failed to load branch reference: {err}"
                    ))
                })
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_iter()
            .map(Head::from_reference)
            .collect::<BTreeSet<Head>>();

        Ok(heads.into_iter().collect())
    }

    /// List all tags in the repository.
    #[getter]
    fn tags(&self) -> PyResult<Vec<Tag>> {
        let platform = self.inner.references().map_err(|err| {
            PyRuntimeError::new_err(format!("Failed to access references: {err}"))
        })?;

        let iter = platform.tags().map_err(|err| {
            PyRuntimeError::new_err(format!("Failed to list tags: {err}"))
        })?;

        let tags: BTreeSet<Tag> = iter
            .map(|reference_result| {
                reference_result.map_err(|err| {
                    PyRuntimeError::new_err(format!("Failed to load tag reference: {err}"))
                })
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_iter()
            .map(Tag::from_reference)
            .collect();

        Ok(tags.into_iter().collect())
    }
}

/// A pure git Python module implemented in Rust.
#[pymodule]
fn gitpure(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Commit>()?;
    m.add_class::<Head>()?;
    m.add_class::<Tag>()?;
    m.add_class::<Repo>()?;
    Ok(())
}
