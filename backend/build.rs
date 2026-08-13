// Roda antes da compilação do crate: lê o .proto e gera o código Rust
// (structs das mensagens + traits do serviço) em OUT_DIR. Por isso o código
// gerado não é versionado — ele nasce do .proto toda vez que se compila.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_prost_build::compile_protos("../proto/placar.proto")?;
    Ok(())
}
