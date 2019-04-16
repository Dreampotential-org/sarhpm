#!/bin/bash

docker-compose -f docker-compose-dev.yml down 
docker-compose -f docker-compose-dev.yml build
sudo cp /opt/var/dev.usepam/settings_local.py ./dprojx/.
docker-compose -f docker-compose-dev.yml up -d

exec "$@"
