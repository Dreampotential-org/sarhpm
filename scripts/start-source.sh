#!/bin/bash

docker-compose -f docker-compose-source.yml down
# docker-compose -f docker-compose-source.yml build
# docker-compose -f docker-compose-source.yml up -d

exec "$@"
