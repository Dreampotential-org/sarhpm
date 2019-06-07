#!/bin/bash

/usr/local/bin/docker-compose -f docker-compose.yml run certbot \
    renew \
    && /usr/local/bin/docker-compose -f docker-compose.yml kill -s SIGHUP web-server

