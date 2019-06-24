#!/bin/sh
cp -r ../dev-useiam/dprojx/static/* static-staging/
exec "$@"
