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
from postgres import mpevidence as pgmp
from elastic import queryAnnsInElastico as es

reload(sys)  
sys.setdefaultencoding('utf8')

#1. pip install psycopg2
#csvfiles = ['data/mp-annotation.tsv']


annsDictCsv = {} ## keep document and count of annotations for validation after load
curr_date = datetime.datetime.now()
dideoDict = {"interact_with": {"id": "-9900001", "code": "DIDEO_00000015"}}

def preprocess(resultsL):

	annsL = []
	for ann in resultsL:		
		## clinicaltrial, statement and case report have required field precipitant
		if ann['method'] in ["Case Report", "DDI clinical trial", "Statement"]: 
			if ann['precipitant'] and ann['drug1'] and ann['drug2']:
				if ann['precipitant'] == 'drug1':
					ann.update({'subject': 'drug1', 'object': 'drug2'})
				elif ann['precipitant'] == 'drug2':
					ann.update({'subject': 'drug2', 'object': 'drug1'})
				else:
					ann.update({'subject': 'drug1', 'object': 'drug2'})
				annsL.append(escapeRow(ann))
				addAnnsToCount(annsDictCsv, ann['document'])
			else:
				print "[ERROR] Precipitant or drug data missing, skip document (%s), claim (%s), method (%s)" % (ann['document'], ann['claimlabel'], ann['method'])		
	
		## phenotype don't have 2nd drug, relationship is inhibits or substrate of
		elif ann['method'] == "Phenotype clinical study":
			if ann['relationship'] in ["inhibits", "substrate of"] and ann['drug1'] and ann['enzyme']:
				if ann['precipitant'] == 'drug1':
					ann.update({'subject': 'drug1', 'object': 'enzyme'})
				elif ann['precipitant'] == 'enzyme':
					ann.update({'subject': 'enzyme', 'object': 'drug1'})
				else:
					ann.update({'subject': 'drug1', 'object': 'drug2'})

				annsL.append(escapeRow(ann))
				addAnnsToCount(annsDictCsv, ann['document'])
			else:
				print "[ERROR] Phenotype clinical study data invalid, skip document (%s), claim (%s), method (%s)" % (ann['document'], ann['claimlabel'], ann['method'])  
		else:
			print "[ERROR] Method undefined, skip document (%s), claim (%s), method (%s)" % (ann['document'], ann['claimlabel'], ann['method'])				

	print "[INFO] total %s annotations are validated and pre-processed" % (len(annsL))

	## write to csv
	csv_columns = ["document", "useremail", "claimlabel", "claimtext", "method", "relationship", "drug1", "drug2", "precipitant", "enzyme", "rejected", "evRelationship", "participants", "participantstext", "drug1dose", "drug1formulation", "drug1duration", "drug1regimens", "drug1dosetext", "drug2dose", "phenotypetype", "phenotypevalue", "phenotypemetabolizer", "phenotypepopulation", "drug2formulation", "drug2duration", "drug2regimens", "drug2dosetext", "aucvalue", "auctype", "aucdirection", "auctext", "cmaxvalue", "cmaxtype", "cmaxdirection", "cmaxtext", "clearancevalue", "clearancetype", "clearancedirection", "clearancetext", "halflifevalue", "halflifetype", "halflifedirection", "halflifetext", "dipsquestion", "reviewer", "reviewerdate", "reviewertotal", "reviewerlackinfo", "grouprandomization", "parallelgroupdesign", "subject", "object", "id"]

	with open('data/preprocess-annotator.csv', 'wb') as f: 
		w = csv.DictWriter(f, csv_columns)
		w.writeheader()
		w.writerows(annsL)

	return annsL


def addAnnsToCount(annsDict, document):
	if document in annsDict:
		annsDict[document] += 1
	else:
		annsDict[document] = 1


def escapeRow(row):

	if row['claimtext']: 
		row['claimtext'] = row['claimtext'].replace("'", "''")
	if row['participantstext']:
		row['participantstext'] = row['participantstext'].replace("'", "''")
	if row['drug1dosetext']:
		row['drug1dosetext'] = row['drug1dosetext'].replace("'", "''")
	if row['drug2dosetext']:
		row['drug2dosetext'] = row['drug2dosetext'].replace("'", "''")
	if row['auctext']:
		row['auctext'] = row['auctext'].replace("'", "''")
	if row['cmaxtext']:
		row['cmaxtext'] = row['cmaxtext'].replace("'", "''")
	if row['clearancetext']:
		row['clearancetext'] = row['clearancetext'].replace("'", "''")
	if row['halflifetext']:
		row['halflifetext'] = row['halflifetext'].replace("'", "''")	

	return row

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



# LOAD MP MATERIAL ################################################################
# load table "mp_material_annotation" and "oa_material_body" one row
def load_mp_material_annotation(conn, row, mp_claim_id, creator, mp_data_index):
	cur = conn.cursor()
	source = row['document']

	if row["drug1dose"] and row["subject"] == "drug1":
		pgmp.insert_material_dose(conn, row, creator, "subject", "drug1", mp_claim_id, mp_data_index)
	if row["drug1dose"] and row["object"] == "drug1":	
		pgmp.insert_material_dose(conn, row, creator, "object", "drug1", mp_claim_id, mp_data_index)
	if row["drug2dose"] and row["subject"] == "drug2":
		pgmp.insert_material_dose(conn, row, creator, "subject", "drug2", mp_claim_id, mp_data_index)
	if row["drug2dose"] and row["object"] == "drug2":	
		pgmp.insert_material_dose(conn, row, creator, "object", "drug2", mp_claim_id, mp_data_index)
	if row['participants'] and row['participants'].lower() != 'unk':
		exact = row['participantstext']
		selector_id = pgmp.insert_oa_selector(conn, '', exact, '')
		target_id = pgmp.insert_oa_target(conn, source, selector_id)	
		material_body_id = pgmp.insert_material_annotation(conn, row, mp_claim_id, target_id, creator, 'participants', mp_data_index)
		pgmp.insert_material_field(conn, row, material_body_id, 'participants')

	if row['phenotypetype']:
		material_body_id = pgmp.insert_material_annotation(conn, row, mp_claim_id, None, creator, 'phenotype', mp_data_index)  
		pgmp.insert_material_field(conn, row, material_body_id, 'phenotype')
		

# LOAD MP DATA ################################################################
# load table "mp_data_annotation" and "oa_data_body" one row
def load_mp_data_annotation(conn, row, mp_claim_id, creator, mp_data_index):
	source = row['document']

	# Clinical trial data items
	if row['aucvalue']:
		exact = row['auctext']
		selector_id = pgmp.insert_oa_selector(conn, '', exact, '')
		target_id = pgmp.insert_oa_target(conn, source, selector_id)		
		data_body_id = pgmp.insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'auc', mp_data_index)
		pgmp.insert_data_field(conn, row, data_body_id, 'auc')

	if row['cmaxvalue']:
		exact = row['cmaxtext']
		selector_id = pgmp.insert_oa_selector(conn, '', exact, '')
		target_id = pgmp.insert_oa_target(conn, source, selector_id)
		data_body_id = pgmp.insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'cmax', mp_data_index)
		pgmp.insert_data_field(conn, row, data_body_id, 'cmax')

	if row['clearancevalue']:
		exact = row['clearancetext']
		selector_id = pgmp.insert_oa_selector(conn, '', exact, '')
		target_id = pgmp.insert_oa_target(conn, source, selector_id)
		data_body_id = pgmp.insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'clearance', mp_data_index)
		pgmp.insert_data_field(conn, row, data_body_id, 'clearance')

	if row['halflifevalue']:
		exact = row['halflifetext']
		selector_id = pgmp.insert_oa_selector(conn, '', exact, '')
		target_id = pgmp.insert_oa_target(conn, source, selector_id)
		data_body_id = pgmp.insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'halflife', mp_data_index)
		pgmp.insert_data_field(conn, row, data_body_id, 'halflife')

	# Case report data items
	if row['reviewer'] and row['reviewerdate']:
		data_body_id = pgmp.insert_mp_data_annotation(conn, row, mp_claim_id, None, creator, 'reviewer', mp_data_index)		
		pgmp.insert_data_field(conn, row, data_body_id, 'reviewer')

	if row['dipsquestion']:
		data_body_id = pgmp.insert_mp_data_annotation(conn, row, mp_claim_id, None, creator, 'dipsquestion', mp_data_index)		
		pgmp.insert_data_field(conn, row, data_body_id, 'dipsquestion')


# LOAD MP CLAIM ################################################################
def load_mp_claim_annotation(conn, row, creator):
	claimP = ""; claimE = row["claimtext"]; claimS = ""
	curr_date = datetime.datetime.now()
	source = row["document"]; claimlabel = row["claimlabel"]

	## when method is statement, negation is evidence supports/refutes
	negation = "No"
	if row["method"] == "Statement":
		if row["evRelationship"] and "refutes" in row["evRelationship"]: 
			negation = False
		else:
			negation = True

	claim_selector_id = pgmp.insert_oa_selector(conn, claimP, claimE, claimS)
	claim_target_id = pgmp.insert_oa_target(conn, source, claim_selector_id)
	oa_claim_body_id = pgmp.insert_oa_claim_body(conn, claimlabel, claimE)

	## subject and object
	if row["subject"] and row["object"]:

		s_drug = row[row["subject"]]
		o_drug = row[row["object"]]

		pgmp.insert_qualifier(conn, "subject", s_drug, None, None, None, None, oa_claim_body_id)
		pgmp.insert_qualifier(conn, "object", o_drug, None, None, None, None, oa_claim_body_id)

	## extran enzyme not in either subject or object
	if row["enzyme"] and "enzyme" not in [row["subject"], row["object"]]:
		e_drug = row["enzyme"] 
		pgmp.insert_qualifier(conn, "enzyme", e_drug, None, None, None, None, oa_claim_body_id)

	pgmp.insert_qualifier(conn, "predicate", row["relationship"], None, None, None, None, oa_claim_body_id)

	## statement rejection 
	rejected = False; rejected_reason = None; rejected_comment = None
	if row["rejected"] and row["rejected"] != "":
		rejected = True
		if '|' in row["rejected"]:
			(rejected_reason, rejected_comment) = row["rejected"].split('|')
		else:
			(rejected_reason, rejected_comment) = [row["rejected"],""]
	
	mp_claim_id = pgmp.insert_mp_claim_annotation(conn, curr_date, oa_claim_body_id, claim_target_id, creator, row['id'], negation, rejected, rejected_reason, rejected_comment)
	pgmp.update_oa_claim_body(conn, mp_claim_id, oa_claim_body_id)
	conn.commit()

	return mp_claim_id


# LOAD MAIN ################################################################
# load annotaitons to postgres
def load_annotations_from_results(conn, results, creator):

	highlightD = {} # drug highlight set in documents {"doc url" : "drug set"}
	curr_date = datetime.datetime.now()

	for row in results:
		annId = row['id']

		# MP Claim - use claim id if exists
		mp_claim_id = pgmp.findClaimIdByAnnId(conn, annId)

		if not mp_claim_id:
			mp_claim_id = load_mp_claim_annotation(conn, row, creator)

		## temp work with AnnotationPress 
		pgmp.insert_method(conn, row, mp_claim_id, 0) 

		mp_data_index = (pgmp.findNumOfDataItems(conn, mp_claim_id) or 0) + 1 

		# MP data
		load_mp_data_annotation(conn, row, mp_claim_id, creator, mp_data_index)
		load_mp_material_annotation(conn, row, mp_claim_id, creator, mp_data_index)

		## method should be 1:1 to data & material and m:1 with claim
		#pgmp.insert_method(conn, row, mp_claim_id, mp_data_index)

		generateHighlightSet(row, highlightD)  # add unique drugs to set
		
	load_highlight_annotation(conn, highlightD, creator)  # load drug highlight annotation
	conn.commit()


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

	results = es.queryAndParseByBody(eshost, esport, qryCondition)

	annsL = preprocess(results)
	load_annotations_from_results(conn, annsL, creator)

	print "[INFO] annotation load completed!"

	if isClean in ["1","2"]:
		print "[INFO] Begin results validating..."
		if test.validateResults(conn, annsDictCsv):
			print "[INFO] all annotations are loaded successfully!"
		else:
			print "[WARN] annotations are loaded incompletely!"


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

	conn = pgconn.connect_postgreSQL(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	load(conn, qryCondition, ES_HOST, ES_PORT, DB_SCHEMA, CREATOR, isClean)
	conn.close()

if __name__ == '__main__':
	main()


