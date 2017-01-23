 # Copyright 2016-2017 University of Pittsburgh

 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at

 #     http:www.apache.org/licenses/LICENSE-2.0

 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.

import sys, csv, json, re
import psycopg2
import uuid
import datetime
from elasticsearch import Elasticsearch
from sets import Set

reload(sys)  
sys.setdefaultencoding('utf8')

######################### VARIABLES ##########################
ES_PORT = 9200

if len(sys.argv) > 2:
	ES_HOSTNAME = str(sys.argv[1])
	INPUT_FILE = str(sys.argv[2])
else:
	print "Usage: loadDomeoAnnsToRDB.py <es hostname> <input file>"
	sys.exit(1)

def getInputDoucuments():
	docL = []
	with open(INPUT_FILE) as f:
		lines = f.read()
		docL = lines.split('\n')
	return Set(docL)

def getAnnotations():
	cntDict = {}

	es = Elasticsearch([{'host': ES_HOSTNAME, 'port': ES_PORT}]) 
	res = es.search(index="annotator", doc_type="annotation", size=100, body={"query":{"match":{"annotationType":"MP"}}})

	print("%d documents found" % res['hits']['total'])

	for doc in res['hits']['hits']:

		if doc['_source']['rawurl'] in cntDict:
			cntDict[doc['_source']['rawurl']] += 1
		else:
			cntDict[doc['_source']['rawurl']] = 1

	return cntDict

def getDocumentWithNoAnnotations():
	resL = []

	resDict = getAnnotations()
	docSet = getInputDoucuments()

	for doc in docSet:
		if doc not in resDict and "http" in doc:
			resL.append(doc)

	return resL
		

######################### MAIN ##########################

def main():
	res = getDocumentWithNoAnnotations()

	print "Documents (%s) in input file (%s) that have not annotation pre-loaded: %s" % (len(res), INPUT_FILE, res)

if __name__ == '__main__':
	main()

		
