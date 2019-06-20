#!/bin/bash

sudo tar cvfz /opt/var/backup/backup-$(date '+%Y-%m-%d-%H-%M').tar.gz /opt/var/media
sudo docker exec -t deploy-prod_db_1 pg_dumpall -c -U postgres > /opt/var/backup/dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
