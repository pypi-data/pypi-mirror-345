// options.rs
use pyo3::prelude::*;
use scirs2_optimize::unconstrained::Options;

/// Options for the Powell optimizer
#[pyclass(name = "Options")]
#[derive(Clone)]
pub struct PyOptions {
    #[pyo3(get, set)]
    pub maxiter: Option<usize>,

    #[pyo3(get, set)]
    pub ftol: Option<f64>,

    #[pyo3(get, set)]
    pub gtol: Option<f64>,

    #[pyo3(get, set)]
    pub eps: Option<f64>,

    #[pyo3(get, set)]
    pub finite_diff_rel_step: Option<f64>,

    #[pyo3(get, set)]
    pub disp: bool,

    #[pyo3(get, set)]
    pub return_all: bool,
}

#[pymethods]
impl PyOptions {
    #[pyo3(signature = (maxiter=None, ftol=None, gtol=None, eps=None, finite_diff_rel_step=None, disp=false, return_all=false))]
    #[new]
    pub fn new(
        maxiter: Option<usize>,
        ftol: Option<f64>,
        gtol: Option<f64>,
        eps: Option<f64>,
        finite_diff_rel_step: Option<f64>,
        disp: Option<bool>,
        return_all: Option<bool>,
    ) -> Self {
        PyOptions {
            maxiter,
            ftol,
            gtol,
            eps,
            finite_diff_rel_step,
            disp: disp.unwrap_or(false),
            return_all: return_all.unwrap_or(false),
        }
    }
}

impl From<PyOptions> for Options {
    fn from(options: PyOptions) -> Self {
        Options {
            maxiter: options.maxiter,
            ftol: options.ftol,
            gtol: options.gtol,
            eps: options.eps,
            finite_diff_rel_step: options.finite_diff_rel_step,
            disp: options.disp,
            return_all: options.return_all,
        }
    }
}

impl From<Options> for PyOptions {
    fn from(options: Options) -> Self {
        PyOptions {
            maxiter: options.maxiter,
            ftol: options.ftol,
            gtol: options.gtol,
            eps: options.eps,
            finite_diff_rel_step: options.finite_diff_rel_step,
            disp: options.disp,
            return_all: options.return_all,
        }
    }
}

impl Default for PyOptions {
    fn default() -> Self {
        Options::default().into()
    }
}
