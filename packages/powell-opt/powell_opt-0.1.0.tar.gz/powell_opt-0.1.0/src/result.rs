// result.rs
use pyo3::prelude::*;
use pyo3::types::PyList;

/// Result of Powell optimization
#[pyclass]
pub struct PyMinimizeResult {
    #[pyo3(get)]
    pub x: Py<PyList>,

    #[pyo3(get)]
    pub fun: f64,

    #[pyo3(get)]
    pub nfev: usize,

    #[pyo3(get)]
    pub nit: usize,

    #[pyo3(get)]
    pub message: String,

    #[pyo3(get)]
    pub success: bool,
}
