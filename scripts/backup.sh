#!/bin/bash
set -xe

export AWS_ACCESS_KEY_ID=AKIAU7EQAGZOF7PQ2HER
export AWS_SECRET_ACCESS_KEY=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
export AWS_DEFAULT_REGION=us-east-2

# create backup dir
BACKUP_DIR=/opt/var/backup/backup-$(date '+%Y-%m-%d-%H-%M')
mkdir $BACKUP_DIR

# backup prod-api
sudo tar cvfz $BACKUP_DIR/backup-media-prod-api-$(date '+%Y-%m-%d-%H-%M').tar.gz /opt/var/media-prod-api
sudo docker exec -t deploy-prod_db_1 pg_dumpall -c -U postgres > $BACKUP_DIR/media-prod-api_dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
sudo tar -cvf $BACKUP_DIR.tar $BACKUP_DIR

aws s3 cp $BACKUP_DIR.tar s3://backups-useiam
rm -fr $BACKUP_DIR
