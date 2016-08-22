#!/bin/bash

# Install jq binary:
# - yum install jq
# - apt-get install jq
# - or download from http://stedolan.github.io/jq/


# Register repo
# $ curl -XPUT 'http://localhost:9200/_snapshot/dbmiannotator_backup' -d '{
#     "type": "fs",
#     "settings": {
#         "location": "/home/yin2/dbmiannotator-backup",
#         "compress": true
#     }
# }'


# Configuration
LIMIT=30  # Number of backups
REPO=dbmiannotator_backup # Name of snapshot repository
PORT=9250  # Elastic port

# Create snapshot
SNAPSHOT=`date +%Y%m%d-%H%M%S`
curl -XPUT "localhost:$PORT/_snapshot/$REPO/$SNAPSHOT?wait_for_completion=true"


# Get a list of snapshots that we want to delete
SNAPSHOTS=`curl -s -XGET "localhost:$PORT/_snapshot/$REPO/_all" \
  | jq -r ".snapshots[:-${LIMIT}][].snapshot"`

# Loop over the results and delete each snapshot
for SNAPSHOT in $SNAPSHOTS
do
 echo "Deleting snapshot: $SNAPSHOT"
 curl -s -XDELETE "localhost:$PORT/_snapshot/$REPO/$SNAPSHOT?pretty"
done
echo "Done!"
