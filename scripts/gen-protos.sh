#!/bin/sh

python -m grpc_tools.protoc -I./submodules/malloy-service/protos --python_out=src/malloy --pyi_out=src/malloy --grpc_python_out=src/malloy ./submodules/malloy-service/protos/**/**/*.proto

echo TODO: Fix src/malloy/services/v1/compiler_pb2_grpc.py import namespace automatically
