// lib.rs
use pyo3::exceptions::PyNotImplementedError;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyList;

use scirs2_optimize::OptimizeError;
use scirs2_optimize::unconstrained::{Method, minimize};

mod options;
mod result;
mod utils;

use options::PyOptions;
use result::PyMinimizeResult;
use utils::{array1_to_py_list, py_list_to_array1};

#[cfg(test)]
mod tests;

/// Python bindings for the Powell optimization method from scirs2-optimize.
#[pymodule]
fn powell_opt(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyOptions>()?;
    m.add_class::<PyMinimizeResult>()?;
    m.add_function(wrap_pyfunction!(powell_minimize, m)?)?;

    Ok(())
}

/// Minimizes a scalar function using Powell's method.
#[pyfunction(name = "minimize")]
#[pyo3(signature = (func, x0, options=None))]
pub fn powell_minimize(
    py: Python,
    func: PyObject,
    x0: PyObject,
    options: Option<PyOptions>,
) -> PyResult<PyMinimizeResult> {
    // Convert x0 to Array1
    let x0_array = py_list_to_array1(x0.bind(py))?;

    // Create options
    let options_struct =
        options.unwrap_or_else(|| PyOptions::new(None, None, None, None, None, None, None));

    // Call the objective function with a Python object
    let call_func = |x: &[f64]| -> f64 {
        // println!("Callback called with x = {:?}", x);
        #[allow(deprecated)]
        let args = PyList::new_bound(py, x);
        match func.call1(py, (args,)) {
            Ok(result) => match result.extract::<f64>(py) {
                Ok(val) => {
                    // println!("Got result: {}", val);
                    val
                }
                Err(e) => {
                    eprintln!("Error extracting function result: {:?}", e);
                    f64::MAX
                }
            },
            Err(e) => {
                eprintln!("Error calling function: {:?}", e);
                f64::MAX
            }
        }
    };

    // Perform the minimization
    let result = minimize(
        call_func,
        &x0_array,
        Method::Powell,
        Some(options_struct.into()),
    )
    .map_err(|e| match e {
        OptimizeError::ComputationError(msg) => PyValueError::new_err(msg),
        OptimizeError::ConvergenceError(msg) => PyRuntimeError::new_err(msg),
        OptimizeError::ValueError(msg) => PyValueError::new_err(msg),
        OptimizeError::NotImplementedError(msg) => {
            PyNotImplementedError::new_err(format!("Not implemented: {}", msg))
        }
    })?;

    // Convert result back to Python types
    let x_py = array1_to_py_list(py, &result.x)?;

    Ok(PyMinimizeResult {
        x: x_py,
        fun: result.fun,
        nfev: result.nfev,
        nit: result.nit,
        message: result.message,
        success: result.success,
    })
}
