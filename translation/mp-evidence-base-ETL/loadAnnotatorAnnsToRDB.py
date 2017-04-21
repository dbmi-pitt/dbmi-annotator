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
import uuid, datetime
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

annsDictCsv = {} ## keep document and count of annotations for validation after load

def addAnnsToCount(annsDict, document):
	if document in annsDict:
		annsDict[document] += 1
	else:
		annsDict[document] = 1


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


# LOAD HIGHLIGHT ANNOTATION ########################################################
def load_highlight_annotation(conn, highlightD, creator):

	for url, drugS in highlightD.iteritems():
		for drug in drugS:
			selector_id = pgmp.insert_oa_selector(conn, "", drug, "")
			target_id = pgmp.insert_oa_target(conn, url, selector_id)
			oa_highlight_body_id = pgmp.insert_oa_highlight_body(conn, drug, url)
			highlight_annotation_id = pgmp.insert_highlight_annotation(conn, type, oa_highlight_body_id, target_id, creator, curr_date, curr_date)
			pgmp.update_oa_highlight_body(conn, highlight_annotation_id, oa_highlight_body_id)


def generateHighlightSet(row, highlightD):

	if not row["subject"] or not row["object"]:
		print row

	subjectDrug = row[row["subject"]]; objectDrug = row[row["object"]]; source = row["document"]
	if source in highlightD:
		highlightD[source].add(subjectDrug)
		highlightD[source].add(objectDrug)
	else:
		highlightD[source] = Set([subjectDrug, objectDrug])


# load annotaitons to postgres
def load_annotations(conn, annotations):

	highlightD = {} # drug highlight set in documents {"doc url" : "drug set"}
	curr_date = datetime.datetime.now()

	for ann in annotations:
		if isinstance(ann, ClinicalTrial):
			load_DDI_CT_annotation(conn, ann)

		## method should be 1:1 to data & material and n:1 with claim
		#method_id = pgmp.insert_method(conn, row, mp_claim_id, mp_data_index)

		#generateHighlightSet(row, highlightD)  # add unique drugs to set
		
	#load_highlight_annotation(conn, highlightD, creator)  # load drug highlight annotation
	conn.commit()


# LOAD MP Annotation ################################################################
def load_DDI_CT_annotation(conn, ann):

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
	
	## insert data
	dmRows = ann.getDataMaterials()
	if dmRows:
		for dmIdx,dmRow in dmRows.items():
			load_DDI_CT_DM(conn, dmRow, mp_claim_id, ann.source, ann.creator)

	conn.commit()
	return mp_claim_id


# LOAD MP ROW OF DATA & MATERIAL  #####################################################
def load_DDI_CT_DM(conn, dmRow, mp_claim_id, source, creator):
	## insert data ratios
	if dmRow.auc:
		load_data_ratio(conn, dmRow.auc, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.cmax:
		load_data_ratio(conn, dmRow.cmax, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.clearance:
		load_data_ratio(conn, dmRow.clearance, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.halflife:
		load_data_ratio(conn, dmRow.halflife, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)

	## insert material participants
	if dmRow.participants:
		load_participants(conn, dmRow.participants, mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)

	## insert material dose
	if dmRow.precipitant_dose:
		load_material_dose(conn, dmRow.precipitant_dose, "precipitant_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)
	if dmRow.object_dose:
		load_material_dose(conn, dmRow.object_dose, "object_dose", mp_claim_id, source, creator, dmRow.dmIdx, dmRow.ev_supports)


# LOAD INDIVIDUAL DATA OR MATERIAL ###################################################
def load_data_ratio(conn, dataRatio, mp_claim_id, source, creator, dmIdx, ev_supports):
	target_id = load_oa_target(conn, source, dataRatio.prefix, dataRatio.exact, dataRatio.suffix) 
	data_body_id = pgmp.insert_data_annotation(conn, mp_claim_id, target_id, creator, dataRatio.field, dmIdx, ev_supports)
	pgmp.insert_data_field(conn, data_body_id, "value", dataRatio.value, None, None)
	pgmp.insert_data_field(conn, data_body_id, "type", dataRatio.type, None, None)
	pgmp.insert_data_field(conn, data_body_id, "direction", dataRatio.direction, None, None)


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


def load_oa_target(conn, source, prefix, exact, suffix):
	selector_id = pgmp.insert_oa_selector(conn, prefix, exact, suffix)
	target_id = pgmp.insert_oa_target(conn, source, selector_id)		
	return target_id



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

	print "[INFO] Begin load data ..."

	annotations = es.getMPAnnsByBody(eshost, esport, qryCondition)
	load_annotations(conn, annotations)
	print "[INFO] annotation load completed!"

	# if isClean in ["1","2"]:
	# 	print "[INFO] Begin results validating..."
	# 	if test.validateResults(conn, annsDictCsv):
	# 		print "[INFO] all annotations are loaded successfully!"
	# 	else:
	# 		print "[WARN] annotations are loaded incompletely!"

def main():

	DB_SCHEMA = "../../db-schema/mp_evidence_schema.sql"
	CREATOR = "DBMI ETL"
	
	PG_DATABASE = 'mpevidence'
	
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



	# ## when method is statement, negation is evidence supports/refutes
	# negation = False
	# ## statement rejection 
	# rejected = False; rejected_reason = None; rejected_comment = None
	# if ann.rejected and ann.rejected != "":
	# 	rejected = True
	# 	if '|' in ann.rejected:
	# 		(rejected_reason, rejected_comment) = ann.rejected.split('|')
	# 	else:
	# 		(rejected_reason, rejected_comment) = [ann.rejected,""]

# LOAD MAIN ################################################################


# def initDideoConceptsDict():

# 	## dict for {concept_code: omop_concept_id}
# 	dideoDict = {"DIDEO_00000015": None, "DIDEO_00000005": None, "OBI_0000427": None, "DIDEO_00000013": None, "DIDEO_00000012": None, "DIDEO_00000093": None, "DIDEO_00000099": None, "DIDEO_00000101": None, "DIDEO_00000100": None, "DIDEO_00000103": None, "DIDEO_00000076": None}

# 	results = subject_concept_code = pgcp.getConceptCodeByVocabId(conn, "DIDEO")
# 	for res in results:
# 		if res[0] and res[1] and res[1] in dideoDict:
# 			dideoDict[res[1]] = res[0]
# 	return dideoDict


# def escapeRow(row):

# 	if row['claimtext']: 
# 		row['claimtext'] = row['claimtext'].replace("'", "''")
# 	if row['participantstext']:
# 		row['participantstext'] = row['participantstext'].replace("'", "''")
# 	if row['drug1dosetext']:
# 		row['drug1dosetext'] = row['drug1dosetext'].replace("'", "''")
# 	if row['drug2dosetext']:
# 		row['drug2dosetext'] = row['drug2dosetext'].replace("'", "''")
# 	if row['auctext']:
# 		row['auctext'] = row['auctext'].replace("'", "''")
# 	if row['cmaxtext']:
# 		row['cmaxtext'] = row['cmaxtext'].replace("'", "''")
# 	if row['clearancetext']:
# 		row['clearancetext'] = row['clearancetext'].replace("'", "''")
# 	if row['halflifetext']:
# 		row['halflifetext'] = row['halflifetext'].replace("'", "''")	

# 	return row
