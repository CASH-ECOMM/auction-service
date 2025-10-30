#!/bin/bash

# Script to generate gRPC Python code from proto files

echo "Generating gRPC code from proto files..."

# Determine Python binary (prefer uv if available, then venv, then system python)
if command -v uv &> /dev/null; then
    PYTHON_CMD="uv run python"
elif [ -d ".venv" ] && [ -x ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -d "venv" ] && [ -x "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD=$(command -v python3 || command -v python)
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python interpreter not found" >&2
    exit 1
fi

# Generate Python code from proto files
$PYTHON_CMD -m grpc_tools.protoc \
    -I./app/proto \
    --python_out=./app/proto \
    --grpc_python_out=./app/proto \
    --pyi_out=./app/proto \
    ./app/proto/auction-service.proto

# Fix imports to use package-relative form for generated gRPC stubs
if [ -f app/proto/auction_service_pb2_grpc.py ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/^import auction_service_pb2/from . import auction_service_pb2/' app/proto/auction_service_pb2_grpc.py
    else
        sed -i 's/^import auction_service_pb2/from . import auction_service_pb2/' app/proto/auction_service_pb2_grpc.py
    fi
fi

echo "gRPC code generation completed successfully!"
