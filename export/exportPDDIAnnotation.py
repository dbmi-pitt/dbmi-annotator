import sys, codecs
sys.path = sys.path + ['.']

## load the library
from elasticsearch import Elasticsearch
import json,csv

## define query conditions
COLLECTION = "annotation"
QUERY_STR = "DDI"

MAX_RESULTS = 10000

def exportAnnotationToCSV():
    ## query elasticsearch on port 9250
    es = Elasticsearch(['http://localhost:9250/'])
    v = es.search(index="annotator",doc_type=COLLECTION, size=MAX_RESULTS)

    #print v['hits']

    with open('annotation.csv','w') as csvfile:
        fieldnames = ['quote','annotationType','created','updated','Drug1',"Drug2"]
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames, quotechar = '"')
        writer.writeheader()

        for jsonCont in v['hits']['hits']:
            print jsonCont['_id']

            jldDict = jsonCont['_source']
            #print jldDict
            if jldDict.has_key('annotationType'):
                if jldDict['annotationType'] == "DDI":
                    writer.writerow({'quote':jldDict['quote'], 'annotationType':jldDict['annotationType'], 'created':jldDict['created'], 'updated':jldDict['updated'], 'Drug1':jldDict['Drug1'], 'Drug2':jldDict['Drug2']})
