#!/bin/bash

docker-compose -f docker-compose-useiam.yml down
docker-compose -f docker-compose-useiam.yml build
docker-compose -f docker-compose-useiam.yml up -d

exec "$@"
