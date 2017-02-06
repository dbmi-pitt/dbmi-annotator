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

import uuid
import datetime
from sets import Set
import sys  
from validate import validateResults
from dbOperations import *

reload(sys)  
sys.setdefaultencoding('utf8')

#1. pip install psycopg2

csvfiles = ['data/mp-annotation.tsv']
DATABASE = 'mpevidence'
curr_date = datetime.datetime.now()
DB_SCHEMA = "../../db-schema/mp_evidence_schema.sql"
CREATOR = "DBMI ETL"

if len(sys.argv) > 5:
	HOSTNAME = str(sys.argv[1])
	PORT = str(sys.argv[2])
	USERNAME = str(sys.argv[3])
	PASSWORD = str(sys.argv[4])
	isClean = str(sys.argv[5])
else:
	print "Usage: loadAnnotatorAnnsToRDB.py <pg hostname> <pg port> <pg username> <pg password> <clean existing data (1: yes, 0: no)>"
	sys.exit(1)

# PRE PROCESS ######################################################################

## add column: subject, object
# rtype: dict with document and count of anns information for validation 
def preprocess(csvfile):

	annsDict = {} ## keep document and count of annotations for validation
 
	csv_columns = ["document", "useremail", "claimlabel", "claimtext", "method", "relationship", "drug1", "drug2", "precipitant", "enzyme", "rejected", "evRelationship", "participants", "participantstext", "drug1dose", "drug1formulation", "drug1duration", "drug1regimens", "drug1dosetext", "drug2dose", "phenotypetype", "phenotypevalue", "phenotypemetabolizer", "phenotypepopulation", "drug2formulation", "drug2duration", "drug2regimens", "drug2dosetext", "aucvalue", "auctype", "aucdirection", "auctext", "cmaxvalue", "cmaxtype", "cmaxdirection", "cmaxtext", "clearancevalue", "clearancetype", "clearancedirection", "clearancetext", "halflifevalue", "halflifetype", "halflifedirection", "halflifetext", "dipsquestion", "reviewer", "reviewerdate", "reviewertotal", "reviewerlackinfo", "grouprandomization", "parallelgroupdesign", "predicate","subject","object", "id"]

	writer = csv.DictWriter(open('data/preprocess-annotator.csv', 'w'), fieldnames=csv_columns)
	writer.writeheader()
	reader = csv.DictReader(utf_8_encoder(open(csvfile, 'r')), delimiter="\t")
	rowsL = []
	for row in reader:		
		## clinicaltrial, statement and case report have required field precipitant
		if row['method'] in ["Case Report", "DDI clinical trial", "Statement"]: 
			if row['precipitant'] != "" and row['drug1'] != "" and row['drug2'] != "":
				if row['precipitant'] == 'drug1':
					row.update({'subject': 'drug1', 'object': 'drug2'})
				elif row['precipitant'] == 'drug2':
					row.update({'subject': 'drug2', 'object': 'drug1'})
				rowsL.append(escapeRow(row))
				addAnnsToCount(annsDict, row['document'])
			else:
				print "[ERROR] Precipitant or drug data missing, skip document (%s), claim (%s), method (%s)" % (row['document'], row['claimlabel'], row['method'])		
	
		## phenotype don't have 2nd drug, relationship is inhibits or substrate of
		elif row['method'] == "Phenotype clinical study":
			if row['relationship'] in ["inhibits", "substrate of"] and row['drug1'] != "" and row['enzyme'] != "":
				row.update({'subject': 'drug1', 'object': 'enzyme'})
				rowsL.append(escapeRow(row))
				addAnnsToCount(annsDict, row['document'])
			else:
				print "[ERROR] Phenotype clinical study data invalid, skip document (%s), claim (%s), method (%s)" % (row['document'], row['claimlabel'], row['method'])	
		
		else:
			print "[ERROR] Method undefined, skip document (%s), claim (%s), method (%s)" % (row['document'], row['claimlabel'], row['method'])				

	print "[INFO] total %s annotations are validated and pre-processed" % (len(rowsL))
	writer.writerows(rowsL)
	return annsDict

def addAnnsToCount(annsDict, document):
	if document in annsDict:
		annsDict[document] += 1
	else:
		annsDict[document] = 1


def escapeRow(row):
	# fix single quote in text
	if "'" in row['claimtext']: 
		row['claimtext'] = row['claimtext'].replace("'", "''")
	if "'" in row['participantstext']:
		row['participantstext'] = row['participantstext'].replace("'", "''")
	if "'" in row['drug1dosetext']:
		row['drug1dosetext'] = row['drug1dosetext'].replace("'", "''")
	if "'" in row['drug2dosetext']:
		row['drug2dosetext'] = row['drug2dosetext'].replace("'", "''")
	if "'" in row['auctext']:
		row['auctext'] = row['auctext'].replace("'", "''")
	if "'" in row['cmaxtext']:
		row['cmaxtext'] = row['cmaxtext'].replace("'", "''")
	if "'" in row['clearancetext']:
		row['clearancetext'] = row['clearancetext'].replace("'", "''")
	if "'" in row['halflifetext']:
		row['halflifetext'] = row['halflifetext'].replace("'", "''")	
	return row

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


# LOAD HIGHLIGHT ANNOTATION ########################################################
def load_highlight_annotation(conn, highlightD, creator):

	for url, drugS in highlightD.iteritems():
		for drug in drugS:
			selector_id = load_oa_selector(conn, "", drug, "")
			target_id = load_oa_target(conn, url, selector_id)
			oa_highlight_body_id = insert_oa_highlight_body(conn, drug, url)
			highlight_annotation_id = insert_highlight_annotation(conn, type, oa_highlight_body_id, target_id, creator, curr_date, curr_date)
			update_oa_highlight_body(conn, highlight_annotation_id, oa_highlight_body_id)


def insert_highlight_annotation(conn, type, has_body, has_target, creator, date_created, date_updated):
	urn = uuid.uuid4().hex
	cur = conn.cursor()

	qry2 = "INSERT INTO highlight_annotation (urn, type, has_body, has_target, creator, date_created, date_updated) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (urn, "all", str(has_body), str(has_target), creator, date_created, date_updated);
	cur.execute(qry2);

	qry2 = "SELECT * FROM highlight_annotation WHERE urn = '%s';" % (urn)
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None

def insert_oa_highlight_body(conn, drug, url):
	urn = uuid.uuid4().hex
	cur = conn.cursor()

	qry1 = "INSERT INTO oa_highlight_body (urn, drugname, uri) VALUES ('%s', '%s', '%s');" % (urn, drug, url);
	cur.execute(qry1);
	
	qry2 = "SELECT * FROM oa_highlight_body WHERE urn = '%s';" % (urn)
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None

def update_oa_highlight_body(conn, highlight_annotation_id, oa_highlight_body_id):
	cur = conn.cursor()
	cur.execute("UPDATE oa_highlight_body SET is_oa_body_of = " + str(highlight_annotation_id) + " WHERE id = " + str(oa_highlight_body_id) + ";")


def generateHighlightSet(row, highlightD):
	subjectDrug = row["subject"]; objectDrug = row["object"]; source = row["document"]
	if source in highlightD:
		highlightD[source].add(subjectDrug)
		highlightD[source].add(objectDrug)
	else:
		highlightD[source] = Set([subjectDrug, objectDrug])


# LOAD METHOD ################################################################
def load_method(conn, row, mp_claim_id, mp_data_index):
	cur = conn.cursor()
	enteredVal = ""
	if row['method'] == "DDI clinical trial":
		enteredVal = "clinical trial"
	elif row['method'] == "Statement":
		enteredVal = "statement"
	else:
		enteredVal = row['method']

	cur.execute("INSERT INTO method (entered_value, inferred_value, mp_claim_id, mp_data_index)" + "VALUES ( '" + enteredVal + "', '" + enteredVal + "', " + str(mp_claim_id) + ", "+str(mp_data_index)+");")

# OPEN ANNOTATION - TARGET AND SELECTOR #############################################
# load table "oa_selector" one row
# input: conn, prefix, exact, suffix
# return: selector id
def load_oa_selector(conn, prefix, exact, suffix):
	cur = conn.cursor()
	urn = uuid.uuid4().hex

	qry1 = "INSERT INTO oa_selector (urn, selector_type, exact, prefix, suffix) VALUES ('%s', '%s', '%s', '%s', '%s');" % (urn, "oa_selector", exact, prefix, suffix)
	cur.execute(qry1)

	qry2 = "SELECT * FROM oa_selector WHERE urn = '%s';" % (urn)
	cur.execute(qry2)

	for row in cur.fetchall():
		return row[0]
	return None

# load table "oa_target" one row
# input: conn, doc source url, selector id
# return: target id
def load_oa_target(conn, source, selector_id):

	cur = conn.cursor()
	urn = uuid.uuid4().hex	

	qry1 = "INSERT INTO oa_target (urn, has_source, has_selector) VALUES ('%s', '%s', '%s');" % (urn, source, selector_id)
	cur.execute(qry1)
	qry2 = "SELECT * FROM oa_target WHERE urn = '%s'" % (urn);
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None

# LOAD QUALIFIER ################################################################
def load_qualifier(conn, qtype, qvalue, concept_code, vocab_id, qtype_concept_code, qtype_vocab_id, claim_body_id):
	cur = conn.cursor()

	s_boo = False; p_boo = False; o_boo = False
	if qtype == "subject":
		s_boo = True
	elif qtype == "predicate":
		p_boo = True
	elif qtype == "object":
		o_boo = True

	cur.execute("""INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, qvalue, concept_code, vocabulary_id, qualifier_type_concept_code, qualifier_type_vocabulary_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (uuid.uuid4().hex, claim_body_id, s_boo, p_boo, o_boo, qvalue, concept_code, vocab_id, qtype_concept_code, qtype_vocab_id))

# LOAD MP MATERIAL ################################################################

## dose_role: subject or object, drug_idx: drug1 or drug2
def load_material_dose(conn, row, creator, dose_role, drug_idx, mp_claim_id, mp_data_index):
	if (row[drug_idx + 'dose'] != ''):
		exact = row[drug_idx + 'dosetext']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, row["document"], selector_id)	
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, target_id, creator, dose_role + "_dose", mp_data_index)				
		load_material_field(conn, row, material_body_id, drug_idx)	


# load table "mp_material_annotation" and "oa_material_body" one row
def load_mp_material_annotation(conn, row, mp_claim_id, creator, mp_data_index):
	cur = conn.cursor()
	source = row['document']

	if row["drug1dose"] != "" and row["subject"] == "drug1":
		load_material_dose(conn, row, creator, "subject", "drug1", mp_claim_id, mp_data_index)
	if row["drug1dose"] != "" and row["object"] == "drug1":	
		load_material_dose(conn, row, creator, "object", "drug1", mp_claim_id, mp_data_index)
	if row["drug2dose"] != "" and row["subject"] == "drug2":
		load_material_dose(conn, row, creator, "subject", "drug2", mp_claim_id, mp_data_index)
	if row["drug2dose"] != "" and row["object"] == "drug2":	
		load_material_dose(conn, row, creator, "object", "drug2", mp_claim_id, mp_data_index)

	if (row['participants'] != '') and (row['participants'].lower() != 'unk'):
		exact = row['participantstext']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)	
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, target_id, creator, 'participants', mp_data_index)
		load_material_field(conn, row, material_body_id, 'participants')

	if (row['phenotypetype'] != ''):
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, None, creator, 'phenotype', mp_data_index)		
		load_material_field(conn, row, material_body_id, 'phenotype')
		

def insert_material_annotation(conn, row, mp_claim_id, has_target, creator, data_type, mp_data_index):
	ev_supports = 'false'
	if 'supports' in row['evRelationship']:
		ev_supports = 'true'

	cur = conn.cursor()
	urn = uuid.uuid4().hex

	cur.execute("INSERT INTO mp_material_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", (urn, data_type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, curr_date))

	cur.execute("SELECT * FROM mp_material_annotation WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		material_annotation_id = result[0]
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO oa_material_body (urn, material_type, is_oa_body_of)" +
				"VALUES ( '" + urn + "', '" + data_type + "', " + str(material_annotation_id) + ");")
	cur.execute("SELECT * FROM oa_material_body WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		has_body = result[0]
	cur.execute("UPDATE mp_material_annotation SET has_body = " + str(has_body) +
				" WHERE id = " + str(material_annotation_id) + ";")
	return has_body


# load table "material_field" one row
def load_material_field(conn, row, material_body_id, material_type):
	cur = conn.cursor()

	if material_type == "participants":
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'participants', NULL, " + row['participants'] + ");")

	elif material_type in ["drug1","drug2"]:
		value = material_type + "dose"
		regimens = material_type + "regimens"
		formulation = material_type + "formulation"
		duration = material_type + "duration"

		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'value', '" + row[value] + "', NULL);")

		if (row[regimens] != '') and (row[regimens].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'regimens', '" + row[regimens] + "', NULL);")
		if (row[formulation] != '') and (row[formulation].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'formulation', '" + row[formulation] + "', NULL);")
		if (row[duration] != '') and (row[duration].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'duration', '" + row[duration] + "', NULL);")

	elif material_type == "phenotype":
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'type', '" + row["phenotypetype"] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'value', '" + row["phenotypevalue"] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'metabolizer', '" + row["phenotypemetabolizer"] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'population', '" + row["phenotypepopulation"] + "', NULL);")		
	else:
		print "[ERROR] material_type (%s) invalid!" % material_type


# LOAD MP DATA ################################################################
# load table "mp_data_annotation" and "oa_data_body" one row
def load_mp_data_annotation(conn, row, mp_claim_id, creator, mp_data_index):
	source = row['document']

	# Clinical trial data items
	if (row['aucvalue'] != '') and (row['aucvalue'].lower() != 'unk'):
		exact = row['auctext']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)		
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'auc', mp_data_index)
		load_data_field(conn, row, data_body_id, 'auc')

	if (row['cmaxvalue'] != '') and (row['cmaxvalue'].lower() != 'unk'):
		exact = row['cmaxtext']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'cmax', mp_data_index)
		load_data_field(conn, row, data_body_id, 'cmax')

	if (row['clearancevalue'] != '') and (row['clearancevalue'].lower() != 'unk'):
		exact = row['clearancetext']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'clearance', mp_data_index)
		load_data_field(conn, row, data_body_id, 'clearance')

	if (row['halflifevalue'] != '') and (row['halflifevalue'].lower() != 'unk'):
		exact = row['halflifetext']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'halflife', mp_data_index)
		load_data_field(conn, row, data_body_id, 'halflife')

	# Case report data items
	if row['reviewer'] != '' and row['reviewerdate'] != '':
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, None, creator, 'reviewer', mp_data_index)		
		load_data_field(conn, row, data_body_id, 'reviewer')

	if row['dipsquestion'] != '':
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, None, creator, 'dipsquestion', mp_data_index)		
		load_data_field(conn, row, data_body_id, 'dipsquestion')

def insert_mp_data_annotation(conn, row, mp_claim_id, has_target, creator, data_type, mp_data_index):
	ev_supports = 'false'
	if 'supports' in row['evRelationship']:
		ev_supports = 'true'

	cur = conn.cursor()
	urn = str(uuid.uuid4().hex)

	cur.execute("""INSERT INTO mp_data_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created, rejected, rejected_reason, rejected_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",(urn ,data_type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, curr_date, None, None, None))

	cur.execute("SELECT * FROM mp_data_annotation WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		data_annotation_id = result[0]
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO oa_data_body (urn, data_type, is_oa_body_of)" +
				"VALUES ( '" + urn + "', '" + data_type + "', " + str(data_annotation_id) + ");")
	cur.execute("SELECT * FROM oa_data_body WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		has_body = result[0]
	cur.execute("UPDATE mp_data_annotation SET has_body = " + str(has_body) +
				" WHERE id = " + str(data_annotation_id) + ";")
	return has_body


# load table "data_field" one row
def load_data_field(conn, row, data_body_id, data_type):
	cur = conn.cursor()

	if data_type in ["auc", "cmax", "clearance", "halflife"]:
		value = data_type + "value"
		ttype = data_type + "type"
		direction = data_type + "direction"

		cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, "value", row[value], None))
		cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, "type", row[ttype], None))
		cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, "direction", row[direction], None))

	if data_type == "reviewer":
		cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'reviewer', '" + row["reviewer"] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'date', '" + row["reviewerdate"] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'total', '" + row["reviewertotal"] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'lackinfo', '" + row["reviewerlackinfo"] + "', NULL);")

	if data_type == "dips":
		dipsQsL = row["dipsquestion"].split('|')
		if dipsQsL and len(dipsQsL) == 10:
			cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q1', '" + dipsQsL[0] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q2', '" + dipsQsL[1] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q3', '" + dipsQsL[2] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q4', '" + dipsQsL[3] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q5', '" + dipsQsL[4] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q6', '" + dipsQsL[5] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q7', '" + dipsQsL[6] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q8', '" + dipsQsL[7] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q9', '" + dipsQsL[8] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q10', '" + dipsQsL[9] + "', NULL);")

# LOAD MP CLAIM ################################################################
# load table "oa_claim_body" one row
# return claim body id
def load_oa_claim_body(conn, claimlabel, exact):
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	
	qry1 = "INSERT INTO oa_claim_body (urn, label, claim_text) VALUES ('%s', '%s', '%s');" % (urn, claimlabel, exact)
	cur.execute(qry1)

	qry2 = "SELECT * FROM oa_claim_body WHERE urn = '%s';" % (urn)
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None


def update_oa_claim_body(conn, is_oa_body_of, oa_claim_body_id):
	cur = conn.cursor()
	cur.execute("UPDATE oa_claim_body SET is_oa_body_of = " + str(is_oa_body_of) +
				" WHERE id = " + str(oa_claim_body_id) + ";")

# insert to table "mp_claim_annotation" 
# return claim annotation id
def insert_mp_claim_annotation(conn, curr_date, has_body, has_target, creator, annId, negation, rejected, rejected_reason, rejected_comment):
	cur = conn.cursor()
	urn = annId

	qry1 = "INSERT INTO mp_claim_annotation (urn, has_body, has_target, creator, date_created, date_updated, negation, rejected_statement, rejected_statement_reason, rejected_statement_comment)" + "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (urn, str(has_body), str(has_target), creator, curr_date, curr_date, negation, rejected, rejected_reason, rejected_comment)

	cur.execute(qry1)
	cur.execute("SELECT * FROM mp_claim_annotation WHERE urn = '" + urn + "';")

	for row in cur.fetchall():
		return row[0]
	return None

def load_mp_claim_annotation(conn, row, creator):
	claimP = ""; claimE = row["claimtext"]; claimS = ""
	curr_date = datetime.datetime.now()
	source = row["document"]; claimlabel = row["claimlabel"]

	## when method is statement, negation is evidence supports/refutes
	negation = "No"
	if row["method"] == "Statement":
		if "refutes" in row["evRelationship"]: 
			negation = True

	claim_selector_id = load_oa_selector(conn, claimP, claimE, claimS)
	claim_target_id = load_oa_target(conn, source, claim_selector_id)
	oa_claim_body_id = load_oa_claim_body(conn, claimlabel, claimE)

	## subject and object
	if row["subject"] and row["object"]:
		s_drug = row[row["subject"]]
		o_drug = row[row["object"]]
		load_qualifier(conn, "subject", s_drug, None, None, None, None, oa_claim_body_id)
		load_qualifier(conn, "object", o_drug, None, None, None, None, oa_claim_body_id)

	## extran enzyme not in either subject or object
	if row["enzyme"] != "" and "enzyme" not in [row["subject"], row["object"]]:
		e_drug = row["enzyme"] 
		load_qualifier(conn, "enzyme", e_drug, None, None, None, None, oa_claim_body_id)

	load_qualifier(conn, "predicate", row["relationship"], None, None, None, None, oa_claim_body_id)

	## statement rejection 
	rejected = False; rejected_reason = None; rejected_comment = None
	if row["rejected"] and row["rejected"] != "":
		rejected = True
		(rejected_reason, rejected_comment) = row["rejected"].split('|')
	
	mp_claim_id = insert_mp_claim_annotation(conn, curr_date, oa_claim_body_id, claim_target_id, creator, row['id'], negation, rejected, rejected_reason, rejected_comment)
	update_oa_claim_body(conn, mp_claim_id, oa_claim_body_id)
	conn.commit()

	return mp_claim_id


def findClaimIdByAnnId(conn, annId):
	cur = conn.cursor()
	cur.execute("SELECT * FROM mp_claim_annotation WHERE urn = '" + annId + "';")

	for row in cur.fetchall():
		return row[0]
	return None

# return the number of data rows for target claim 
# return 0 if no data avaliable
def findNumOfDataItems(conn, claimId):
	cur = conn.cursor()
	qry = """	
	select max(dann.mp_data_index)
	from mp_data_annotation dann
	where dann.mp_claim_id = %s
	""" % (claimId)

	cur = conn.cursor()
	cur.execute(qry)
		
	for row in cur.fetchall():
		return row[0]
	return 0

# LOAD MAIN ################################################################
def load_data_from_csv(conn, reader, creator):

	highlightD = {} # drug highlight set in documents {"doc url" : "drug set"}
	curr_date = datetime.datetime.now()

	for row in reader:
		annId = row['id']

		# MP Claim - use claim id if exists
		mp_claim_id = findClaimIdByAnnId(conn, annId)
		if not mp_claim_id:
			mp_claim_id = load_mp_claim_annotation(conn, row, creator)

		mp_data_index = (findNumOfDataItems(conn, mp_claim_id) or 0) + 1 

		# MP data
		load_mp_data_annotation(conn, row, mp_claim_id, creator, mp_data_index)
		load_mp_material_annotation(conn, row, mp_claim_id, creator, mp_data_index)
		load_method(conn, row, mp_claim_id, mp_data_index)

		generateHighlightSet(row, highlightD)  # add unique drugs to set
		
	load_highlight_annotation(conn, highlightD, creator)  # load drug highlight annotation
	conn.commit()

def main():

	conn = connect_postgreSQL(HOSTNAME, USERNAME, PASSWORD, DATABASE)

	if isClean == "1":
		clearall(conn)
		conn.commit()
		print "[INFO] Clean all tables done!"
	elif isClean == "2":
		truncateall(conn) # delete all tables in DB mpevidence
		conn.commit()
		createdb(conn, DB_SCHEMA)
		conn.commit()
		print "[INFO] Drop and recreate all tables done!"
	
	print "[INFO] Begin load data ..."
	for csvfile in csvfiles:
		annsDictCsv = preprocess(csvfile)
		reader = csv.DictReader(utf_8_encoder(open('data/preprocess-annotator.csv', 'r')))
		load_data_from_csv(conn, reader, CREATOR)

	print "[INFO] annotation load completed!"
	print "[INFO] Begin results validating..."

	if validateResults(conn, annsDictCsv):
		print "[INFO] all annotations are loaded successfully!"
	else:
		print "[WARN] annotations are loaded incompletely!"
	conn.close()

if __name__ == '__main__':
	main()


