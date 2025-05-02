use std::env;
use std::error::Error;
use std::path::PathBuf;
use walkdir::WalkDir;

fn main() -> Result<(), Box<dyn Error>> {
    // Get absolute path of workspace root
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR")?);
    let workspace_root = manifest_dir
        .parent()
        .ok_or("No parent directory")?
        .parent()
        .ok_or("No parent directory")?
        .parent()
        .ok_or("No workspace root")?;

    // Construct absolute path to proto directory
    let proto_dir = workspace_root.join("proto");
    let proto_dir = proto_dir
        .canonicalize()
        .map_err(|e| format!("Failed to canonicalize proto dir: {}", e))?;
    let proto_dir_str = proto_dir.to_str().ok_or("Invalid proto dir path")?;

    // Debug information
    println!("Workspace root: {}", workspace_root.display());
    println!("Proto dir path: {}", proto_dir.display());

    // Find all .proto files
    let mut proto_files = Vec::new();
    for entry in WalkDir::new(&proto_dir)
        .follow_links(true)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        if entry.path().extension() == Some(std::ffi::OsStr::new("proto")) {
            let proto_path = entry
                .path()
                .canonicalize()
                .map_err(|e| format!("Failed to canonicalize proto file path: {}", e))?;
            let proto_path_str = proto_path.to_str().ok_or("Invalid proto file path")?;

            // Print found proto file
            println!("Found proto file: {}", proto_path.display());
            // Add to rerun-if-changed
            println!("cargo:rerun-if-changed={}", proto_path_str);
            proto_files.push(proto_path_str.to_string());
        }
    }

    if proto_files.is_empty() {
        return Err(format!("No .proto files found in: {}", proto_dir_str).into());
    }

    // Convert proto_files to slice of str
    let proto_files_str: Vec<&str> = proto_files.iter().map(|s| s.as_str()).collect();

    // Configure proto compilation - output directly to src directory
    prost_build::Config::new()
        .out_dir("src") // Changed from "src/proto" to "src"
        .protoc_arg("--experimental_allow_proto3_optional")
        .compile_protos(&proto_files_str, &[proto_dir_str])
        .map_err(|e| format!("Failed to compile protos: {}", e))?;

    Ok(())
}
