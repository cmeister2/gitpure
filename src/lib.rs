use pyo3::exceptions::PyRuntimeError;
use pyo3::{prelude::*, types::PyType};
use std::path::Path;

#[pyclass(unsendable)]
struct Repo {
    inner: gix::Repository,
}

#[pymethods]
impl Repo {
    /// The path to the `.git` directory of the repository.
    #[getter]
    fn git_dir(&self, py: Python) -> PyResult<PyObject> {
        let git_dir_path = self.inner.git_dir();
        let pathlib = py.import("pathlib")?;
        let path_class = pathlib.getattr("Path")?;
        let path_obj = path_class.call1((git_dir_path.as_os_str(),))?;
        Ok(path_obj.into())
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
}

/// A pure git Python module implemented in Rust.
#[pymodule]
fn gitpure(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Repo>()?;
    Ok(())
}
