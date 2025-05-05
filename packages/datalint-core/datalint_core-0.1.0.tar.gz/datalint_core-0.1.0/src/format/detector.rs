use crate::format::types::DatasetFormat;
use std::fs;
use std::path::Path;

pub fn get_dataset_format(dataset_path: &Path) -> Option<DatasetFormat> {
    if let Some(format) = is_coco_format(dataset_path) {
        return Some(format);
    }
    // TODO: implement other format checks

    None
}

fn is_coco_format(dataset_path: &Path) -> Option<DatasetFormat> {
    let annotations_path = dataset_path.join("annotations");
    if annotations_path.exists() && annotations_path.is_dir() {
        for entry in fs::read_dir(&annotations_path).ok()? {
            let entry = entry.ok()?;
            let file_name = entry.file_name();
            if let Some(name) = file_name.to_str() {
                if name.ends_with(".json") && name.contains("instances") {
                    return Some(DatasetFormat::COCOJson);
                }
            }
        }
    }
    None
}
