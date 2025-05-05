use std::fs;
use std::path::PathBuf;

pub fn list_files_recursive(dir: &PathBuf) -> Vec<PathBuf> {
    let mut files = vec![];
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                files.extend(list_files_recursive(&path));
            } else {
                files.push(path);
            }
        }
    }
    files
}
