use pyo3::prelude::*;

mod format;
mod py;
mod utils;

pub use format::{get_dataset_format, validate_format, DatasetFormat};

// PyO3 function registration macro
macro_rules! register_pyfunctions {
    ($module:ident, [$($func:ident),* $(,)?]) => {
        $(
            $module.add_function(wrap_pyfunction!($func, &$module)?)?;
        )*
    };
}

#[pymodule]
fn datalint_core(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    use py::*;
    register_pyfunctions!(m, [py_get_dataset_format, py_validate_dataset_format,]);
    Ok(())
}
