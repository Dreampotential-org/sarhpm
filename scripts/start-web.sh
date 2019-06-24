#!/bin/bash

cp -r ../dev-useiam/dprojx/static/* ../static-staging/

docker-compose -f docker-compose-web.yml down
docker-compose -f docker-compose-web.yml build
docker-compose -f docker-compose-web.yml up -d

exec "$@"
