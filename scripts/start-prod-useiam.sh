#!/bin/bash

docker-compose -f docker-compose-prod-useiam.yml down
docker-compose -f docker-compose-prod-useiam.yml build
docker-compose -f docker-compose-prod-useiam.yml up -d

exec "$@"
