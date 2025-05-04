// utils.rs
use ndarray::Array1;
use pyo3::prelude::*;
use pyo3::types::PyList;

/// Convert a Python list-like object to Array1
pub fn py_list_to_array1(list: &Bound<'_, PyAny>) -> PyResult<Array1<f64>> {
    // Use downcast() instead of extract
    let list = list.downcast::<PyList>()?;
    let mut vec = Vec::with_capacity(list.len());

    for item in list.iter() {
        let value = item.extract::<f64>()?;
        vec.push(value);
    }

    Ok(Array1::from(vec))
}

/// Convert a Rust ndarray to a Python list
pub fn array1_to_py_list(py: Python<'_>, array: &Array1<f64>) -> PyResult<Py<PyList>> {
    #[allow(deprecated)]
    let list = PyList::new_bound(py, array.iter().copied());
    // Convert Bound to Py
    Ok(list.into())
}
