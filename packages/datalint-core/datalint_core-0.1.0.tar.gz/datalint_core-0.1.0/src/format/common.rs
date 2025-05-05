use std::path::PathBuf;

pub fn is_json_file(file: &PathBuf) -> bool {
    file.extension().map_or(false, |ext| ext == "json")
}
