#!/bin/bash

/usr/local/bin/docker-compose -f docker-compose-web.yml run certbot \
    renew \
    && /usr/local/bin/docker-compose -f docker-compose-web.yml kill -s SIGHUP web-server

