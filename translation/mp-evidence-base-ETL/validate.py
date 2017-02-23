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
def createAnnForTesting(conn, template, annUrn):
	CREATOR = "ETL Tester"
	
	## clean postgres
	pgmp.clearAll(conn)
	conn.commit()

	## clean test samples in elasticsearch
	# if exists, then delete
	# es.deleteById("localhost", "9200", annUrn)

	## load test ann to elasticsearch
	annotation = loadTemplateInJson(template)
	es.createMpAnnotation("localhost", "9200", annotation, annUrn)

	## query elasticsearch for annotation sample
	results = es.queryAndParseById("localhost", "9200", annUrn)
	## translate and load to postgres
	annsL = pgload.preprocess(results)
	pgload.load_annotations_from_results(conn, annsL, CREATOR)

	## qry postgres for validating individual annotation
	annotation = pgqry.queryMpAnnotationByUrn(conn, annUrn)
	return annotation


## TESTING FUNCTIONS ######################################################
def testClaim(annotation, urn, label, csubject, cpredicate, cobject, exact, method, negation, rejected):
	print "[INFO] begin validating claim qualifiers..."
	if isMatched("subject", csubject, annotation.csubject) and isMatched("predicate", cpredicate, annotation.cpredicate) and isMatched("object", cobject, annotation.cobject):
		print "[TEST] claim qualifiers is validated"
	else:
		print "[ERROR] claim qualifiers are not correct"

	print "[INFO] begin validating claim..."
	if isMatched("label", label, annotation.label) and isMatched("exact text", exact, annotation.exact) and isMatched("user entered method", method, annotation.method) and isMatched("negation", negation, annotation.negation) and isMatched("rejected", rejected, annotation.rejected):
		print "[TEST] claim is validated"		
	else:
		print "[ERROR] claim is not correct"

def testDataRatio(dataItem, ratiotype, value, type, direction, exact):
	print "[INFO] begin validating %s..." % ratiotype
	if isMatched("value", value, dataItem.value) and isMatched("type", type,dataItem.type) and isMatched("direction", direction,dataItem.direction) and isMatched("exact text", exact, dataItem.exact):
		print "[TEST] %s is validated" % (ratiotype)
	else:
		print "[ERROR] %s is incorrect" % (ratiotype)

def testMaterialDose(doseItem, dosetype, value, formulation, duration, regimens, exact):
	print "[INFO] begin validating %s..." % dosetype
	if isMatched("dose type", dosetype, doseItem.field) and isMatched("value", value, doseItem.value) and isMatched("duration", duration, doseItem.duration) and isMatched("formulation", formulation, doseItem.formulation) and isMatched("regimens", regimens, doseItem.regimens) and isMatched("exact text", exact, doseItem.exact):
		print "[TEST] %s is validated" % (dosetype)
	else:
		print "[ERROR] %s is incorrect" % (dosetype)

def testParticipants(partItem, value, exact):
	print "[INFO] begin validating participants..."
	if isMatched("participants", value, partItem.value) and isMatched("participants", exact, partItem.exact):
		print "[TEST] participants is validated"
	else:
		print "[ERROR] participants is incorrect"

def testEvRelationship(value1, value2):
	if isMatched("evidence relationship", value1, value2):
		print "[TEST] evidence relationship is validated"
	else:
		print "[ERROR] evidence relationship is incorrect"		

def testPhenotype(phenoItem, ptype, value, metabolizer, population):
	print "[INFO] begin validating phenotype..."
	if isMatched("phenotype", ptype, phenoItem.ptype) and isMatched("value", value, phenoItem.value) and isMatched("metabolizer", metabolizer, phenoItem.metabolizer) and isMatched("population", population, phenoItem.population):
		print "[TEST] phenotype is validated"
	else:
		print "[ERROR] phenotype is incorrect"

def testDataReviewer(reviewerItem, reviewer, date, total, lackinfo):
	print "[INFO] begin validating data reviewer..."
	if isMatched("reviewer", reviewer, reviewerItem.reviewer) and isMatched("date", date, reviewerItem.date) and isMatched("total", total, reviewerItem.total) and isMatched("lackinfo", lackinfo, reviewerItem.lackinfo):
		print "[TEST] data reviewer is validated"
	else:
		print "[ERROR] data reviewer is incorrect"


def testDataDipsQs(dipsItem, qsDict):
	print "[INFO] begin validating dips questions..."
	annDipsQsDict = dipsItem.getDipsDict()
	if len(annDipsQsDict) == len(qsDict):
		for k,v in qsDict.iteritems():
			if not isMatched("dips " + k, v, annDipsQsDict[k]):
				return
		print "[TEST] dips questions are validated"
	else:
		print "[ERROR] incorrect number of dips questions"

def isMatched(field, val1, val2):
	if type(val1) != type(val2):
		print "[ERROR] %s have an incorrect data type" % field
		return False

	if val1 == val2:
		#print "[TEST] %s is validated" % field
		return True
	
	print "[ERROR] %s is incorrect: val1 (%s) and val2 (%s)" % (field, val1, val2)
	return False	

## TESTING CASES #############################################################
# Validate clinical trial annotation 
# Two data & material items

def test_clinical_trial_1(conn, template):
	print "[INFO] =====begin test clinical trial annotation 1 ======================"

	annotationUrn = "test-case-id-1"
	annotation = createAnnForTesting(conn, template, annotationUrn)
	mpDataMaterialD = annotation.getDataMaterials()

	## claim validation
	print "[INFO] ================= Begin validating MP Claim ======================"
	testClaim(annotation, "test-case-id-1", "telaprevir_inhibits_atorvastatin", "atorvastatin", "inhibits", "telaprevir", "claim-text", "DDI clinical trial", False, "rejected-reason|rejected-comment")

	print "[INFO] ================= Begin validating MP data ======================="
	## data 1 validation
	dmRow1 = mpDataMaterialD[1]
	testEvRelationship(dmRow1.getEvRelationship(), "supports")
	auc1 = dmRow1.getDataRatioItemInRow("auc")
	testDataRatio(auc1, "AUC ratio", "7.88", "Fold", "Increase", "auc-text-1")
	cmax1 = dmRow1.getDataRatioItemInRow("cmax")
	testDataRatio(cmax1, "Cmax ratio", "10.6", "Fold", "Increase", "cmax-text-1")
	clearance1 = dmRow1.getDataRatioItemInRow("clearance")
	testDataRatio(clearance1, "Clearance ratio", "87.8", "Percent", "Decrease", "clearance-text-1")
	halflife1 = dmRow1.getDataRatioItemInRow("halflife")
	testDataRatio(halflife1, "Halflife ratio", "28.5", "Percent", "Decrease", "halflife-text-1")
	## material 1 validation	
	partMaterial1 = dmRow1.getParticipantsInRow()
	testParticipants(partMaterial1, "21.00", "participants-text-1")
	subjectdose1 = dmRow1.getMaterialDoseInRow("subject_dose")
	testMaterialDose(subjectdose1, "subject_dose", "30", "Oral", "1", "SD", "drug2Dose-text-1")
	objectdose1 = dmRow1.getMaterialDoseInRow("object_dose")
	testMaterialDose(objectdose1, "object_dose", "20", "Oral", "16", "Q8", "drug1Dose-text-1")

	## data 2 validation
	dmRow2 = mpDataMaterialD[2]
	testEvRelationship(dmRow2.getEvRelationship(), "refutes")
	auc2 = dmRow2.getDataRatioItemInRow("auc")
	testDataRatio(auc2, "AUC ratio", "17.88", "Percent", "Decrease", "auc-text-2")
	cmax2 = dmRow2.getDataRatioItemInRow("cmax")
	testDataRatio(cmax2, "Cmax ratio", "10.3", "Percent", "Decrease", "cmax-text-2")
	clearance2 = dmRow2.getDataRatioItemInRow("clearance")
	testDataRatio(clearance2, "Clearance ratio", "7.8", "Fold", "Increase", "clearance-text-2")
	halflife2 = dmRow2.getDataRatioItemInRow("halflife")
	testDataRatio(halflife2, "Halflife ratio", "2.5", "Fold", "Increase", "halflife-text-2")
	## material 2 validation
	partMaterial2 = dmRow2.getParticipantsInRow()
	testParticipants(partMaterial2, "210.00", "participants-text-2")
	subjectdose2 = dmRow2.getMaterialDoseInRow("subject_dose")
	testMaterialDose(subjectdose2, "subject_dose", "302", "Oral", "10", "BID", "drug2Dose-text-2")
	objectdose2 = dmRow2.getMaterialDoseInRow("object_dose")
	testMaterialDose(objectdose2, "object_dose", "201", "Oral", "120", "Q3", "drug1Dose-text-2")

def test_phenotype_clinical_study_1(conn, template):
	print "[INFO] =====begin test phenotype clinical study annotation 1 ============"

	annotationUrn = "test-case-id-2"
	annotation = createAnnForTesting(conn, template, annotationUrn)
	mpDataMaterialD = annotation.getDataMaterials()

	## claim validation
	print "[INFO] ================= Begin validating MP Claim ======================"
	testClaim(annotation, "test-case-id-2", "drugname1_substrate of_enzyme1", "enzyme1", "substrate of", "drugname1", "claim-text", "Phenotype clinical study", False, "rejected-reason|rejected-comment")

	## data 1 validation
	print "[INFO] ================= Begin validating MP data ======================="
	dmRow1 = mpDataMaterialD[1]
	testEvRelationship(dmRow1.getEvRelationship(), "refutes")
	auc1 = dmRow1.getDataRatioItemInRow("auc")
	testDataRatio(auc1, "AUC ratio", "1.2", "Fold", "Increase", "auc-text-1")
	cmax1 = dmRow1.getDataRatioItemInRow("cmax")
	testDataRatio(cmax1, "Cmax ratio", "1.6", "Percent", "Increase", "cmax-text-1")
	clearance1 = dmRow1.getDataRatioItemInRow("clearance")
	testDataRatio(clearance1, "Clearance ratio", "8.8", "Percent", "Increase", "clearance-text-1")
	halflife1 = dmRow1.getDataRatioItemInRow("halflife")
	testDataRatio(halflife1, "Halflife ratio", "2.5", "Percent", "Decrease", "halflife-text-1")

	## material 1 validation
	partMaterial1 = dmRow1.getParticipantsInRow()
	testParticipants(partMaterial1, "1.00", "participants-text-1")
	phenoItem = dmRow1.getPhenotype()
	testPhenotype(phenoItem, "Genotype", "BRAF", "Poor Metabolizer", "Asian")
	objectdose1 = dmRow1.getMaterialDoseInRow("object_dose")
	testMaterialDose(objectdose1, "object_dose", "10", "IV", "23", "Q6", "drug1Dose-text-1")
	
def test_case_report_1(conn, template):
	print "[INFO] =====begin test case report annotation 1 ============"

	annotationUrn = "test-case-id-3"
	annotation = createAnnForTesting(conn, template, annotationUrn)

	## claim validation
	print "[INFO] ================= Begin validating MP Claim ======================"
	testClaim(annotation, "test-case-id-3", "drugname1_interact with_drugname2", "drugname1", "interact with", "drugname2", "claim-text", "Case Report", False, "test-reason|test-comment")

	print "[INFO] ================= Begin validating MP data ======================="
	dmRow1 = annotation.getSpecificDataMaterial(1)
	reviewerItem1 = dmRow1.getDataReviewer()
	testDataReviewer(reviewerItem1, "External","02/22/2017", "-1", "False")
	dipsItem1 = dmRow1.getDataDips()
	testDataDipsQs(dipsItem1, {"q1":"Yes","q2":"Yes","q10":"No","q3":"No","q4":"No","q5":"NA","q6":"UNK/NA","q7":"UNK/NA","q8":"No","q9":"NA"})

	partMaterial1 = dmRow1.getParticipantsInRow()
	testParticipants(partMaterial1, "1.00", "participants-text-1")
	subjectdose1 = dmRow1.getMaterialDoseInRow("subject_dose")
	testMaterialDose(subjectdose1, "subject_dose", "13", "IV", "22", "Q6", "drug1Dose-text-1")
	objectdose1 = dmRow1.getMaterialDoseInRow("object_dose")
	testMaterialDose(objectdose1, "object_dose", "56", "IV", "65", "Q6", "drug2Dose-text-1")


def validate():

	PG_HOST = "localhost"
	PG_USER = "dbmiannotator"
	PG_PASSWORD = "dbmi2016"
	PG_DATABASE = "mpevidence"

	conn = pgconn.connect_postgreSQL(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	## "DDI clinical trial", "Phenotype clinical study", "Case Report", "Statement"

	MP_ANN_1 = "./template/test-annotation-1.json"
	test_clinical_trial_1(conn, MP_ANN_1)

	MP_ANN_2 = "./template/test-annotation-2.json"
	test_phenotype_clinical_study_1(conn, MP_ANN_2)

	MP_ANN_3 = "./template/test-annotation-3.json"
	test_case_report_1(conn, MP_ANN_3)

	conn.close()


## MAIN ######################################################
if __name__ == '__main__':
	validate()

