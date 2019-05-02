#!/bin/bash

docker-compose -f docker-compose-app-useiam.yml down
docker-compose -f docker-compose-app-useiam.yml build
docker-compose -f docker-compose-app-useiam.yml up -d

exec "$@"
