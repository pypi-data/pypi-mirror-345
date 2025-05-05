use crate::format::{get_dataset_format, validate_format, DatasetFormat};
use pyo3::prelude::*;
use std::path::Path;

#[pyfunction(name = "get_dataset_format")]
pub fn py_get_dataset_format(path: String) -> Option<String> {
    let path = Path::new(&path);
    get_dataset_format(path).map(|f| format!("{:?}", f))
}

#[pyfunction(name = "validate_dataset_format")]
pub fn py_validate_dataset_format(path: String, format_str: String) -> PyResult<()> {
    let format = match format_str.as_str() {
        "COCOJson" => DatasetFormat::COCOJson,
        "YOLOObjectDetection" => DatasetFormat::YOLOObjectDetection,
        "YOLOSegmentation" => DatasetFormat::YOLOSegmentation,
        "YOLOOBB" => DatasetFormat::YOLOOBB,
        "PascalVOCXml" => DatasetFormat::PascalVOCXml,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Unknown dataset format",
            ))
        }
    };

    validate_format(Path::new(&path), &format)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
}
