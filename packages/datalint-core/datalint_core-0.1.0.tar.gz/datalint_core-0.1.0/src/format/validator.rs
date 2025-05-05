use super::types::DatasetFormat;
use std::fs;
use std::path::Path;

pub fn validate_format(dataset_path: &Path, format: &DatasetFormat) -> Result<(), String> {
    match format {
        DatasetFormat::COCOJson => validate_coco(dataset_path),
        _ => Err(format!("Validation for {:?} not implemented yet.", format)),
    }
}

fn validate_coco(dataset_path: &Path) -> Result<(), String> {
    let annotations_path = dataset_path.join("annotations");
    if !annotations_path.exists() {
        return Err("Missing 'annotations' directory.".into());
    }

    let mut has_valid_json = false;
    for entry in fs::read_dir(&annotations_path).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let file_name = entry.file_name();
        if let Some(name) = file_name.to_str() {
            if name.ends_with(".json") && name.contains("instances") {
                has_valid_json = true;
                break;
            }
        }
    }

    if !has_valid_json {
        return Err("No valid COCO instances JSON file found in 'annotations'.".into());
    }

    Ok(())
}
