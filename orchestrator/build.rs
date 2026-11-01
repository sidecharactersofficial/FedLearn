// Generates Rust bindings from ../proto (the single source of truth).
fn main() -> std::io::Result<()> {
    let protoc = protoc_bin_vendored::protoc_bin_path().expect("vendored protoc not found");
    std::env::set_var("PROTOC", protoc);

    let root = "../proto";
    let files: Vec<String> = ["config.proto", "result.proto", "observation.proto"]
        .iter()
        .map(|f| format!("{root}/fedids/v1/{f}"))
        .collect();

    prost_build::compile_protos(&files, &[root])?;
    println!("cargo:rerun-if-changed={root}");
    Ok(())
}
