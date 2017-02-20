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

import sys, csv, json, re, os, uuid
import datetime
from sets import Set

from postgres import connection as pgconn
from postgres import mpevidence as pgmp
from postgres import query as pgqry

from elastic import queryAnnsInElastico as es

import loadAnnotatorAnnsToRDB as pgload

reload(sys)  
sys.setdefaultencoding('utf8')

## VALIDATE TOTAL ANNOTATIONS TRANSLATE AND LOAD #############################
## validate query results and the results from csv
## rttype: boolean
def validateResults(conn, csvD):
	rdbD = queryDocAndDataCnt(conn)	

	# print csvD
	# print "======================================="
	# print rdbD

	return compareTwoDicts(csvD, rdbD)

## query MP claim, rtype: dict with document url and counts of annotation
def queryDocAndDataCnt(conn):
	claimDict = {}

	qry = """
set schema 'ohdsi';
select distinct t.has_source, cann.urn, max(dann.mp_data_index)
from mp_claim_annotation cann join oa_claim_body cbody on cann.has_body = cbody.id
join oa_target t on cann.has_target = t.id
left join mp_data_annotation dann on cann.id = dann.mp_claim_id
group by t.has_source, cann.urn
order by t.has_source, cann.urn """

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():
		document = row[0]; claim_urn = row[1]; cnt = row[2]

		if not cnt or cnt == "":
			cnt = 1

		if document in claimDict:				
			claimDict[document] += cnt
		else:
			claimDict[document] = cnt

	return claimDict

## compare two dicts
## rtype: boolean (same: True, different: False)
def compareTwoDicts(dict1, dict2):

	if not dict1 or not dict2:
		print "[ERROR] empty annotation set during validating"
		return False

	if len(dict1) != len(dict2):
		print "[ERROR] the number of annotations from csv not the same as from postgresDB"
		return False

	for k,v in dict1.iteritems():
		if k in dict2 and dict2[k] == v:
			print "[INFO] document (%s) have MP data (%s) validated" % (k, v)
		else:
			print "[ERROR] document (%s) have MP data (%s) from dict1 but data (%s) from dict 2" % (k, v, dict2[k])
			return False
	return True
	

# load json template
def loadTemplateInJson(path):
	json_data=open(path)

	data = json.load(json_data)
	json_data.close()
	return data

	
## VALIDATE INDIVIDUAL ANNOTATION TRANSLATE AND LOAD #############################
def validateAnnotation(conn):
	ES_HOST = "localhost"
	ES_PORT = "9200"
	DB_SCHEMA = "../../db-schema/mp_evidence_schema.sql"
	CREATOR = "DBMI ETL"

	URL = "http://localhost/PMC/PMC000000.html"
	annotationUrn = "test-case-id-1"

	## clean test samples
	es.deleteById(ES_HOST, ES_PORT, annotationUrn)

	## load test ann to elasticsearch
	MP_ANN_1 = "./template/test-annotation-1.json"
	annotation = loadTemplateInJson(MP_ANN_1)
	es.createMpAnnotation(ES_HOST, ES_PORT, annotation, annotationUrn)

	## query elasticsearch for annotation sample
	results = es.queryAndParseById(ES_HOST, ES_PORT, annotationUrn)

	## translate and load to postgres
	annsL = pgload.preprocess(results)
	pgload.load_annotations_from_results(conn, annsL, CREATOR)

	## qry postgres for validating individual annotation
	annotation = pgqry.queryMpAnnotationByUrn(conn, annotationUrn)
	
	print annotation.claimid
	print annotation.urn

	print annotation.exact
	print annotation.label
	print annotation.method

	print annotation.csubject
	print annotation.cpredicate
	print annotation.cobject

	mpDataMaterialD = annotation.getDataMaterials()

	data1 = mpDataMaterialD[1]
	auc = data1.getDataItemInRow("auc")
	print auc.value


def validate():

	PG_HOST = "localhost"
	PG_USER = "dbmiannotator"
	PG_PASSWORD = "dbmi2016"
	PG_DATABASE = "mpevidence"

	conn = pgconn.connect_postgreSQL(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")
	validateAnnotation(conn)

	conn.close()

if __name__ == '__main__':
	validate()

