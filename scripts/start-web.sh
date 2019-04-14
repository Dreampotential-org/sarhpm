#!/bin/bash

docker-compose -f docker-compose-web.yml down 
docker-compose -f docker-compose-web.yml build
docker-compose -f docker-compose-web.yml up -d

exec "$@"
