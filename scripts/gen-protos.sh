#!/bin/sh

python -m grpc_tools.protoc -I./submodules/malloy-service/protos --python_out=src/malloy --pyi_out=src/malloy --grpc_python_out=src/malloy ./submodules/malloy-service/protos/**/**/*.proto
sed -i '' -e "s/from services.v1/from malloy.services.v1/g" src/malloy/services/v1/compiler_pb2_grpc.py