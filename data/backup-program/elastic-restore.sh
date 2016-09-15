#!/bin/bash
#
# Restore a snapshot 

# Configuration
SNAPSHOT=20160822-164139
REPO=dbmiannotator_backup # Name of snapshot repository
PORT=9250
INDEX=annotator

# Close the index
curl -XPOST 'http://localhost:$PORT/$INDEX/_close'

# Restore the snapshot 
curl -XPOST 'http://localhost:$PORT/_snapshot/$REPO/$SNAPSHOT/_restore'

# Re-open the index
curl -XPOST 'http://localhost:$PORT/$INDEX/_open'
