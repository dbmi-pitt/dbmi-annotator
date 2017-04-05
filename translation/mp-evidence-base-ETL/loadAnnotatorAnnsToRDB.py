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

import csv
import datetime
from sets import Set
import sys  
import validate as test

from postgres import connection as pgconn
from postgres import mpEvidenceLoad as pgmp
from postgres import omopConceptQry as pgcp
from elastic import queryMPAnnotation as es
from model.Micropublication import *

reload(sys)  
sys.setdefaultencoding('utf8')

annsDictCsv = {} # keep document and count of annotations for validation after load
drugMapD = {} # concept as {"concept name": Concept}

# load annotaitons to postgres
def load_annotations(conn, annotations, creator):

	highlightD = {} # drug highlight set in documents {"doc url" : "drug set"}
	curr_date = datetime.datetime.now()

	for ann in annotations:
		load_annotation(conn, ann, creator)
		generateHighlightSet(ann, highlightD)  # add unique drugs to set		
	load_highlight_annotations(conn, highlightD, creator)  # load drug highlight annotation
	conn.commit()


def load_annotation(conn, annotation, creator):
	if isinstance(annotation, ClinicalTrial):
		load_ClinicalTrial_annotation(conn, annotation)
	elif isinstance(annotation, Statement):
		load_Statement_annotation(conn, annotation)
	elif isinstance(annotation, PhenotypeClinicalStudy):
		load_PhenClinicalStudy_annotation(conn, annotation)
	elif isinstance(annotation, CaseReport):
		load_CaseReport_annotation(conn, annotation)


# LOAD HIGHLIGHT ANNOTATION ########################################################
def load_highlight_annotations(conn, highlightD, creator):
	curr_date = datetime.datetime.now()
	for url, drugS in highlightD.iteritems():
		for drug in drugS:
			selector_id = pgmp.insert_oa_selector(conn, "", drug, "")
			target_id = pgmp.insert_oa_target(conn, url, selector_id)
			oa_highlight_body_id = pgmp.insert_oa_highlight_body(conn, drug, url)
			highlight_annotation_id = pgmp.insert_highlight_annotation(conn, oa_highlight_body_id, target_id, creator, curr_date, curr_date)
			pgmp.update_oa_highlight_body(conn, highlight_annotation_id, oa_highlight_body_id)


## add unique qualifiers by article to highlight dict for load
# param1: Annotation  
# param2: dict for highlight_annotaiton article_highlight as True
def generateHighlightSet(annotation, highlightD):
	source = annotation.source; sDrug = None; oDrug = None; qDrug = None

	sQualifier = annotation.csubject
	if sQualifier.isDrugProduct():
		sDrug = sQualifier.qvalue
	oQualifier = annotation.cobject
	if oQualifier.isDrugProduct():
		oDrug = oQualifier.qvalue		
	if annotation.cqualifier:
		qQualifier = annotation.cqualifier
		if qQualifier.isDrugProduct():
			qDrug = qQualifier.qvalue

	if source not in highlightD:
		highlightD[source] = Set([])

	if sDrug:
		highlightD[source].add(sDrug)
	if oDrug:
		highlightD[source].add(oDrug) 
	if qDrug:
		highlightD[source].add(qDrug)


def addAnnsToCount(annsDict, document):
	if document in annsDict:
		annsDict[document] += 1
	else:
		annsDict[document] = 1


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


# LOAD Clinical Trial Annotation ####################################################
def load_ClinicalTrial_annotation(conn, ann):

	## insert mp_claim_annotation, oa_claim_body
	claim_target_id = load_oa_target(conn, ann.source, ann.prefix, ann.exact, ann.suffix)
	claim_body_id = pgmp.insert_claim_body(conn, ann.label, ann.exact)
	mp_claim_id = pgmp.insert_claim_annotation(conn, ann, claim_body_id, claim_target_id, False)
	pgmp.update_claim_body(conn, mp_claim_id, claim_body_id)

	## insert qualifiers
	pgmp.insert_qualifier(conn, ann.csubject, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cpredicate, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cobject, claim_body_id)		
	if ann.cqualifier:
		pgmp.insert_qualifier(conn, ann.cqualifier, claim_body_id)
	
	dmRows = ann.getDataMaterials()
	if dmRows:
		for dmIdx,dmRow in dmRows.items():
			load_method_DM(conn, ann.method, ann.method, dmRow, dmIdx, mp_claim_id) # insert method
			load_ClinicalTrial_DM(conn, dmRow, mp_claim_id, ann.source, ann.creator) # insert data and material
	else:
		load_method_DM(conn, ann.method, ann.method, None, None, mp_claim_id) # insert method
	return mp_claim_id


def load_ClinicalTrial_DM(conn, dmRow, mp_claim_id, source, creator):
	## insert data
	if dmRow.auc:
		load_data_ratio(conn, dmRow.auc, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.cmax:
		load_data_ratio(conn, dmRow.cmax, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.clearance:
		load_data_ratio(conn, dmRow.clearance, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.halflife:
		load_data_ratio(conn, dmRow.halflife, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)

	## insert material
	if dmRow.participants:
		load_participants(conn, dmRow.participants, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.precipitant_dose:
		load_material_dose(conn, dmRow.precipitant_dose, "precipitant_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.object_dose:
		load_material_dose(conn, dmRow.object_dose, "object_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)


# LOAD Phenotype Clinical Study Annotation ##########################################
def load_PhenClinicalStudy_annotation(conn, ann):

	## insert mp_claim_annotation, oa_claim_body
	claim_target_id = load_oa_target(conn, ann.source, ann.prefix, ann.exact, ann.suffix)
	claim_body_id = pgmp.insert_claim_body(conn, ann.label, ann.exact)
	mp_claim_id = pgmp.insert_claim_annotation(conn, ann, claim_body_id, claim_target_id, False)
	pgmp.update_claim_body(conn, mp_claim_id, claim_body_id)

	## insert qualifiers
	pgmp.insert_qualifier(conn, ann.csubject, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cpredicate, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cobject, claim_body_id)		
	
	dmRows = ann.getDataMaterials()
	if dmRows:
		for dmIdx,dmRow in dmRows.items():
			load_method_DM(conn, ann.method, ann.method, dmRow, dmIdx, mp_claim_id) # insert method
			load_PhenClinicalStudy_DM(conn, dmRow, mp_claim_id, ann.source, ann.creator) # load data & material
	else:
		load_method_DM(conn, ann.method, ann.method, None, None, mp_claim_id) # insert method		

	return mp_claim_id


def load_PhenClinicalStudy_DM(conn, dmRow, mp_claim_id, source, creator):
	## insert data
	if dmRow.auc:
		load_data_ratio(conn, dmRow.auc, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.cmax:
		load_data_ratio(conn, dmRow.cmax, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.clearance:
		load_data_ratio(conn, dmRow.clearance, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.halflife:
		load_data_ratio(conn, dmRow.halflife, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)

	## insert material
	if dmRow.participants:
		load_participants(conn, dmRow.participants, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.probesubstrate_dose:
		load_material_dose(conn, dmRow.probesubstrate_dose, "probesubstrate_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.phenotype:
		load_material_phenotype(conn, dmRow.phenotype, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)


# LOAD Case Report Annotation ####################################################
def load_CaseReport_annotation(conn, ann):

	## insert mp_claim_annotation, oa_claim_body
	claim_target_id = load_oa_target(conn, ann.source, ann.prefix, ann.exact, ann.suffix)
	claim_body_id = pgmp.insert_claim_body(conn, ann.label, ann.exact)
	mp_claim_id = pgmp.insert_claim_annotation(conn, ann, claim_body_id, claim_target_id, False)
	pgmp.update_claim_body(conn, mp_claim_id, claim_body_id)

	## insert qualifiers
	pgmp.insert_qualifier(conn, ann.csubject, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cpredicate, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cobject, claim_body_id)		
	
	dmRows = ann.getDataMaterials()
	if dmRows:
		for dmIdx,dmRow in dmRows.items():
			pgmp.insert_method(conn, ann.method, ann.method, mp_claim_id, dmIdx) # load method
			load_CaseReport_DM(conn, dmRow, mp_claim_id, ann.source, ann.creator) # insert data & material
	else:
		pgmp.insert_method(conn, ann.method, ann.method, mp_claim_id, None) # load method
	return mp_claim_id


def load_CaseReport_DM(conn, dmRow, mp_claim_id, source, creator):

	## insert data
	if dmRow.reviewer:
		load_data_reviewer(conn, dmRow.reviewer, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.dipsquestion:
		load_data_dipsquestion(conn, dmRow.dipsquestion, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)

	## insert material
	if dmRow.precipitant_dose:
		load_material_dose(conn, dmRow.precipitant_dose, "precipitant_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.object_dose:
		load_material_dose(conn, dmRow.object_dose, "object_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)


# LOAD Statement Annotation #########################################################
def load_Statement_annotation(conn, ann):

	## insert mp_claim_annotation, oa_claim_body
	claim_target_id = load_oa_target(conn, ann.source, ann.prefix, ann.exact, ann.suffix)
	claim_body_id = pgmp.insert_claim_body(conn, ann.label, ann.exact)
	mp_claim_id = pgmp.insert_claim_annotation(conn, ann, claim_body_id, claim_target_id, ann.negation)
	pgmp.update_claim_body(conn, mp_claim_id, claim_body_id)

	## insert qualifiers
	pgmp.insert_qualifier(conn, ann.csubject, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cpredicate, claim_body_id)
	pgmp.insert_qualifier(conn, ann.cobject, claim_body_id)		
	if ann.cqualifier:
		pgmp.insert_qualifier(conn, ann.cqualifier, claim_body_id)

	load_method_DM(conn, ann.method, ann.method, None, 0, mp_claim_id) # insert method
	
	conn.commit()
	return mp_claim_id


# LOAD Method AND EV type related questions ##########################################
def load_method_DM(conn, entered_method, inferred_method, dmRow, dmIdx, mp_claim_id):
	method_id = pgmp.insert_method(conn, entered_method, inferred_method, mp_claim_id, dmIdx)	
	if dmRow:
		if dmRow.parallelgroup:
			pgmp.insert_evidence_question(conn, "parallelgroup", dmRow.parallelgroup, method_id)
		if dmRow.grouprandom:
			pgmp.insert_evidence_question(conn, "grouprandom", dmRow.grouprandom, method_id)


# LOAD INDIVIDUAL DATA OR MATERIAL ###################################################
def load_data_ratio(conn, dataRatio, mp_claim_id, source, creator, dmIdx, ev_supports):
	target_id = load_oa_target(conn, source, dataRatio.prefix, dataRatio.exact, dataRatio.suffix) 
	data_body_id = pgmp.insert_data_annotation(conn, mp_claim_id, target_id, creator, dataRatio.field, dmIdx, ev_supports)
	pgmp.insert_data_field(conn, data_body_id, "value", dataRatio.value, None, None)
	pgmp.insert_data_field(conn, data_body_id, "type", dataRatio.type, None, None)
	pgmp.insert_data_field(conn, data_body_id, "direction", dataRatio.direction, None, None)


def load_data_reviewer(conn, revItem, mp_claim_id, source, creator, dmIdx, ev_supports):
	data_body_id = pgmp.insert_data_annotation(conn, mp_claim_id, None, creator, "reviewer", dmIdx, ev_supports)	
	pgmp.insert_data_field(conn, data_body_id, "reviewer", revItem.reviewer, None, None)
	pgmp.insert_data_field(conn, data_body_id, "date", revItem.date, None, None)
	pgmp.insert_data_field(conn, data_body_id, "total", revItem.total, None, None)
	pgmp.insert_data_field(conn, data_body_id, "lackinfo", revItem.lackinfo, None, None)


def load_data_dipsquestion(conn, dipsItem, mp_claim_id, source, creator, dmIdx, ev_supports):
	dipsD = dipsItem.getDipsDict()
	data_body_id = pgmp.insert_data_annotation(conn, mp_claim_id, None, creator, "dipsquestion", dmIdx, ev_supports)
	for qs, val in dipsD.iteritems():
		pgmp.insert_data_field(conn, data_body_id, qs, val, None, None)


def load_participants(conn, partItem, mp_claim_id, source, creator, dmIdx, ev_supports):
	target_id = load_oa_target(conn, source, partItem.prefix, partItem.exact, partItem.suffix) 
	material_body_id = pgmp.insert_material_annotation(conn, mp_claim_id, target_id, creator, "participants", dmIdx, ev_supports)
	pgmp.insert_material_field(conn, material_body_id, "value", partItem.value, None, None)


def load_material_dose(conn, matDose, material_dose_type, mp_claim_id, source, creator, dmIdx, ev_supports):
	target_id = load_oa_target(conn, source, matDose.prefix, matDose.exact, matDose.suffix)
	material_body_id = pgmp.insert_material_annotation(conn, mp_claim_id, target_id, creator, material_dose_type, dmIdx, ev_supports)
	pgmp.insert_material_field(conn, material_body_id, "value", matDose.value, None, None)
	pgmp.insert_material_field(conn, material_body_id, "drugname", matDose.drugname, None, None)
	pgmp.insert_material_field(conn, material_body_id, "duration", matDose.duration, None, None)
	pgmp.insert_material_field(conn, material_body_id, "formulation", matDose.formulation, None, None)
	pgmp.insert_material_field(conn, material_body_id, "regimens", matDose.regimens, None, None)


def load_material_phenotype(conn, phenoItem, mp_claim_id, source, creator, dmIdx, ev_supports):
	target_id = load_oa_target(conn, source, phenoItem.prefix, phenoItem.exact, phenoItem.suffix) 
	material_body_id = pgmp.insert_material_annotation(conn, mp_claim_id, target_id, creator, "phenotype", dmIdx, ev_supports)
	pgmp.insert_material_field(conn, material_body_id, "type", phenoItem.ptype, None, None)
	pgmp.insert_material_field(conn, material_body_id, "value", phenoItem.value, None, None)
	pgmp.insert_material_field(conn, material_body_id, "metabolizer", phenoItem.metabolizer, None, None)
	pgmp.insert_material_field(conn, material_body_id, "population", phenoItem.population, None, None)


def load_oa_target(conn, source, prefix, exact, suffix):
	selector_id = pgmp.insert_oa_selector(conn, prefix, exact, suffix)
	target_id = pgmp.insert_oa_target(conn, source, selector_id)		
	return target_id


## MAIN #############################################################################
def load(conn, qryCondition, eshost, esport, dbschema, creator, isClean):

	if isClean == "1":
		pgmp.clearAll(conn)
		conn.commit()
		print "[INFO] Clean all tables done!"
	elif isClean == "2":
		pgmp.truncateAll(conn) # delete all tables in DB mpevidence
		conn.commit()
		pgconn.createdb(conn, dbschema)
		conn.commit()
		print "[INFO] Drop and recreate all tables done!"

	annotations = es.getMPAnnsByBody(eshost, esport, qryCondition)

	print "[INFO] Begin translate and load mp annotations (%s)" % len(annotations)
	load_annotations(conn, annotations, creator)

	print "[INFO] annotation load completed!"

	# if isClean in ["1","2"]:
	# 	print "[INFO] Begin results validating..."
	# 	if test.validateResults(conn, annsDictCsv):
	# 		print "[INFO] all annotations are loaded successfully!"
	# 	else:
	# 		print "[WARN] annotations are loaded incompletely!"

def main():

	DB_SCHEMA = "../../db-schema/mp_evidence_schema.sql"
	CREATOR = "dbmi.etl@gmail.com"; PG_DATABASE = 'mpevidence'
	
	if len(sys.argv) > 7:
		ES_HOST = str(sys.argv[1])
		ES_PORT = str(sys.argv[2])
		PG_HOST = str(sys.argv[3])
		PG_PORT = str(sys.argv[4])
		PG_USER = str(sys.argv[5])
		PG_PASSWORD = str(sys.argv[6])
		isClean = str(sys.argv[7])
	else:
		print "Usage: python loadAnnotatorAnnsToRDB.py <elastic host> <elastic port> <pg host> <pg port> <pg username> <pg password> <OPTIONS (1: clean all tables, 2 drop and recreate all tables, 0: keep existing data)>"
		sys.exit(1)

	qryCondition = {'query': { 'term': {'annotationType': 'MP'}}}
	# qryCondition = {"query": {"bool": 
	# 	{"must": [
	# 		{"term": {"rawurl": "http://localhost/PMC/PMC3187007.html"}},
	# 		{"term": {"annotationType": "MP"}}
	# 	]
	#  }}}

	conn = pgconn.connect_postgres(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	load(conn, qryCondition, ES_HOST, ES_PORT, DB_SCHEMA, CREATOR, isClean)
	conn.close()

if __name__ == '__main__':
	main()

