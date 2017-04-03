from elasticsearch import Elasticsearch
import sys, csv, json, os, uuid

## create customized document based on template
## rtype null
def createMpAnnotation(host, port, annotation, annotationId):
	es = Elasticsearch([{'host': host, 'port': port}]) 
	es.index(index="annotator", doc_type="annotation", id=annotationId, body=json.dumps(annotation))

## query documents by json format query condition
## rtype json documents
def queryByBody(host, port, doc):
	es = Elasticsearch([{'host': host, 'port': port}])
	res = es.search(index="annotator", size="5000", body=doc)	
	return res

def queryById(host, port, annotationId):
	es = Elasticsearch([{'host': host, 'port': port}])
	res = es.get(index="annotator", id = annotationId)	
	return res

## delete document by id
## rtype null
def deleteById(host, port, annotationId):
	es = Elasticsearch([{'host': host, 'port': port}])
	es.delete(index="annotator", doc_type="annotation", id=annotationId)
