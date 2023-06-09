#!/bin/sh

pushd ./submodules/malloy-service

npm run build && npm run package

popd

cp -r submodules/malloy-service/pkg/@malloydata/* src/malloy/service
