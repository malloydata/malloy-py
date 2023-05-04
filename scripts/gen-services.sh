#!/bin/sh

cd ../malloy-service

npm run build && npm run package

cd $OLDPWD

cp -r ../malloy-service/pkg/@malloydata/* src/malloy/service