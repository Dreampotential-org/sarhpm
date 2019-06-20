#!/bin/bash

docker-compose -f docker-compose-dev-useiam.yml down
docker-compose -f docker-compose-dev-useiam.yml build
docker-compose -f docker-compose-dev-useiam.yml up -d

exec "$@"
