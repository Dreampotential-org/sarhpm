#!/bin/bash

/usr/local/bin/docker-compose -f docker-compose-web.yml run certbot \
    certonly --webroot --webroot-path=/var/www/html --email aaronorosen@gmail.com \
    --agree-tos --no-eff-email --force-renewal -d $1 
