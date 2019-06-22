#!/bin/bash

docker-compose -f docker-compose-urbanrecovery.yml down
docker-compose -f docker-compose-urbanrecovery.yml build
docker-compose -f docker-compose-urbanrecovery.yml up -d

exec "$@"
