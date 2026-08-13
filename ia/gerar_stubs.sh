#!/usr/bin/env bash
# Gera os stubs Python a partir de proto/placar.proto.
# Rode sempre que o .proto mudar (o lado Rust regenera sozinho no cargo build).
set -euo pipefail

cd "$(dirname "$0")/.."

python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=ia/gerado \
    --grpc_python_out=ia/gerado \
    proto/placar.proto

touch ia/gerado/__init__.py

# O protoc gera "import placar_pb2", um import absoluto que só funciona se o
# diretório dos stubs estiver no sys.path. Como aqui eles são importados como
# pacote (ia.gerado), o import precisa ser relativo.
sed -i 's/^import placar_pb2 as placar__pb2$/from . import placar_pb2 as placar__pb2/' \
    ia/gerado/placar_pb2_grpc.py

echo "stubs gerados em ia/gerado/"
