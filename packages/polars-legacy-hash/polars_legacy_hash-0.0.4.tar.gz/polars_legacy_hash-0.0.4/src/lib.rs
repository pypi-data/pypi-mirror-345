mod expressions;
mod pl_legacy_hashing;

use pyo3::types::PyModule;
use pyo3::{pymodule, PyResult, Python};
// use pyo3_polars::PolarsAllocator;
//
// #[global_allocator]
// static ALLOC: PolarsAllocator = PolarsAllocator::new();
// TODO why inject the python in rust? two things to keep in sync?
#[pymodule]
fn _internal(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
