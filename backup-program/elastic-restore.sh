#!/bin/bash
#
# Restore a snapshot 

# Configuration

REPO=dbmiannotator-elastic-snapshot # Name of snapshot repository

HOST=$1
PORT=$2
SNAPSHOT=$3

if [[ -z $HOST || -z $PORT || -z $SNAPSHOT ]]; then
   echo "Usage: bash elastic-restore.sh <hostname> <port> <snapshot name>"
   echo "ex. bash elastic-restore.sh localhost 9200 20160822-164139"
   exit
else
    INDEX=annotator

    # Close the index
    curl -XPOST "http://$HOST:$PORT/$INDEX/_close"

    # Restore the snapshot 
    curl -XPOST "http://$HOST:$PORT/_snapshot/$REPO/$SNAPSHOT/_restore"
    
    # Re-open the index
    curl -XPOST "http://$HOST:$PORT/$INDEX/_open"
    echo "Restore snapshot - Done!"
fi

