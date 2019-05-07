#!/bin/bash

docker-compose -f docker-compose-urbanrecovery-useiam.yml down
docker-compose -f docker-compose-urbanrecovery-useiam.yml build
docker-compose -f docker-compose-urbanrecovery-useiam.yml up -d

exec "$@"
