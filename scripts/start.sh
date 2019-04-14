#!/bin/bash

docker-compose -f docker-compose-staging.yml down 
docker-compose -f docker-compose-staging.yml build
docker-compose -f docker-compose-staging.yml up -d

exec "$@"
