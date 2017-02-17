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

import psycopg2
import uuid, datetime

curr_date = datetime.datetime.now()

def setDbSchema(conn, name):
	cur = conn.cursor()
	cur.execute("SET SCHEMA '" + name + "';")


# QUALIFIER ################################################################
def insert_qualifier(conn, qtype, qvalue, concept_code, vocab_id, qtype_concept_code, qtype_vocab_id, claim_body_id):
	cur = conn.cursor()

	s_boo = False; p_boo = False; o_boo = False
	if qtype == "subject":
		s_boo = True
	elif qtype == "predicate":
		p_boo = True
	elif qtype == "object":
		o_boo = True

	cur.execute("""INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, qvalue, concept_code, vocabulary_id, qualifier_type_concept_code, qualifier_type_vocabulary_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (uuid.uuid4().hex, claim_body_id, s_boo, p_boo, o_boo, qvalue, concept_code, vocab_id, qtype_concept_code, qtype_vocab_id))


# OPEN ANNOTATION - TARGET AND SELECTOR #############################################
# load table "oa_selector" one row
# input: conn, prefix, exact, suffix
# return: selector id
def insert_oa_selector(conn, prefix, exact, suffix):
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
def insert_oa_target(conn, source, selector_id):

	cur = conn.cursor()
	urn = uuid.uuid4().hex	

	qry1 = "INSERT INTO oa_target (urn, has_source, has_selector) VALUES ('%s', '%s', '%s');" % (urn, source, selector_id)
	cur.execute(qry1)
	qry2 = "SELECT * FROM oa_target WHERE urn = '%s'" % (urn);
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None

# MP CLAIM ########################################################
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


# load table "oa_claim_body" one row
# return claim body id
def insert_oa_claim_body(conn, claimlabel, exact):
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


# MP MATERIAL ########################################################
## dose_role: subject or object, drug_idx: drug1 or drug2
def insert_material_dose(conn, row, creator, dose_role, drug_idx, mp_claim_id, mp_data_index):
	if row[drug_idx + 'dose']:
		exact = row[drug_idx + 'dosetext']
		selector_id = insert_oa_selector(conn, '', exact, '')
		target_id = insert_oa_target(conn, row["document"], selector_id)	
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, target_id, creator, dose_role + "_dose", mp_data_index)				
		insert_material_field(conn, row, material_body_id, drug_idx)	


def insert_material_annotation(conn, row, mp_claim_id, has_target, creator, data_type, mp_data_index):
	ev_supports = True
	if "evRelationship" in row and row['evRelationship']:
		if 'refutes' in row['evRelationship']:
			ev_supports = False

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
def insert_material_field(conn, row, material_body_id, material_type):
	cur = conn.cursor()

	if material_type == "participants":
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'participants', NULL, " + row['participants'] + ");")

	elif material_type in ["drug1","drug2"]:
		value = material_type + "dose"
		regimens = material_type + "regimens"
		formulation = material_type + "formulation"
		duration = material_type + "duration"

		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'value', '" + row[value] + "', NULL);")

		if row[regimens] and row[regimens].lower() != 'unk':
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'regimens', '" + row[regimens] + "', NULL);")
		if row[formulation] and (row[formulation].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'formulation', '" + row[formulation] + "', NULL);")
		if row[duration] and (row[duration].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'duration', '" + row[duration] + "', NULL);")

	elif material_type == "phenotype":
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s,%s,%s,%s,%s)",(uuid.uuid4().hex, str(material_body_id),'type',row["phenotypetype"],None))
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s,%s,%s,%s,%s)",(uuid.uuid4().hex, str(material_body_id),'value',row["phenotypevalue"],None))
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s,%s,%s,%s,%s)",(uuid.uuid4().hex, str(material_body_id),'metabolizer',row["phenotypemetabolizer"],None))
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s,%s,%s,%s,%s)",(uuid.uuid4().hex, str(material_body_id),'population',row["phenotypepopulation"],None))
	else:
		print "[ERROR] material_type (%s) invalid!" % material_type



# MP DATA ########################################################

def insert_mp_data_annotation(conn, row, mp_claim_id, has_target, creator, data_type, mp_data_index):

	ev_supports = 'true'
	if "evRelationship" in row and row["evRelationship"]:
		if 'refutes' in row['evRelationship']:
			ev_supports = 'false'

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
def insert_data_field(conn, row, data_body_id, data_type):
	cur = conn.cursor()

	if data_type in ["auc", "cmax", "clearance", "halflife"]:
		value = data_type + "value"
		ttype = data_type + "type"
		direction = data_type + "direction"

		cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, "value", row[value], None))
		cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, "type", row[ttype], None))
		cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, "direction", row[direction], None))

	if data_type == "reviewer":
		cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'reviewer', '" + (row["reviewer"] or "") + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'date', '" + (row["reviewerdate"] or "") + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'total', '" + (str(row["reviewertotal"]) or "") + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'lackinfo', '" + (str(row["reviewerlackinfo"]) or "") + "', NULL);")

	if data_type == "dipsquestion" and "undefined" not in row["dipsquestion"]:
		dipsQsL = row["dipsquestion"].split('|')

		if dipsQsL and len(dipsQsL) == 10:
			cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q1', '" + dipsQsL[0] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q2', '" + dipsQsL[1] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q3', '" + dipsQsL[2] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q4', '" + dipsQsL[3] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q5', '" + dipsQsL[4] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q6', '" + dipsQsL[5] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q7', '" + dipsQsL[6] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q8', '" + dipsQsL[7] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q9', '" + dipsQsL[8] + "', NULL), ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'q10', '" + dipsQsL[9] + "', NULL);")

# HIGHLIGHT ANNOTATION ########################################################
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


# MP METHOD ################################################################
def insert_method(conn, row, mp_claim_id, mp_data_index):
	cur = conn.cursor()
	enteredVal = ""
	if row['method'] == "DDI clinical trial":
		enteredVal = "clinical trial"
	elif row['method'] == "Statement":
		enteredVal = "statement"
	else:
		enteredVal = row['method']

	cur.execute("INSERT INTO method (entered_value, inferred_value, mp_claim_id, mp_data_index)" + "VALUES ( '" + enteredVal + "', '" + enteredVal + "', " + str(mp_claim_id) + ", "+str(mp_data_index)+");")


def findClaimIdByAnnId(conn, annId):
	cur = conn.cursor()
	cur.execute("SET SCHEMA 'ohdsi';")
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

# UTILS ################################################################
def truncateAll(conn):
	cur = conn.cursor()
	cur.execute("DROP TABLE IF EXISTS qualifier;")
	cur.execute("DROP TABLE IF EXISTS oa_claim_body;")
	cur.execute("DROP TABLE IF EXISTS oa_selector;")
	cur.execute("DROP TABLE IF EXISTS oa_target;")
	cur.execute("DROP TABLE IF EXISTS data_field;")
	cur.execute("DROP TABLE IF EXISTS oa_data_body;")
	cur.execute("DROP TABLE IF EXISTS mp_data_annotation;")
	cur.execute("DROP TABLE IF EXISTS material_field;")
	cur.execute("DROP TABLE IF EXISTS oa_material_body;")
	cur.execute("DROP TABLE IF EXISTS mp_material_annotation;")
	cur.execute("DROP TABLE IF EXISTS method;")
	cur.execute("DROP TABLE IF EXISTS claim_reference_relationship;")
	cur.execute("DROP TABLE IF EXISTS mp_reference;")
	cur.execute("DROP TABLE IF EXISTS mp_claim_annotation;")
	cur.execute("DROP TABLE IF EXISTS oa_highlight_body;")
	cur.execute("DROP TABLE IF EXISTS highlight_annotation;")

	cur.execute("DROP SEQUENCE IF EXISTS mp_claim_annotation_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_selector_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_target_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_claim_body_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS qualifier_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS mp_data_annotation_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_data_body_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS data_field_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS mp_material_annotation_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_material_body_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS material_field_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS method_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS claim_reference_relationship_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS mp_reference_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS highlight_annotation_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_highlight_body_id_seq;")

def clearAll(conn):
	cur = conn.cursor()
	#cur.execute("ALTER TABLE mp_data_annotation DROP CONSTRAINT mp_data_annotation_mp_claim_id_fkey")
	cur.execute("SET SCHEMA 'ohdsi';")
	cur.execute("DELETE FROM qualifier;")
	cur.execute("DELETE FROM oa_claim_body;")
	cur.execute("DELETE FROM oa_selector;")
	cur.execute("DELETE FROM oa_target;")
	cur.execute("DELETE FROM data_field;")
	cur.execute("DELETE FROM oa_data_body;")
	cur.execute("DELETE FROM mp_data_annotation;")
	cur.execute("DELETE FROM material_field;")
	cur.execute("DELETE FROM oa_material_body;")
	cur.execute("DELETE FROM mp_material_annotation;")
	cur.execute("DELETE FROM method;")
	cur.execute("DELETE FROM mp_claim_annotation;")
	cur.execute("DELETE FROM oa_highlight_body;")
	cur.execute("DELETE FROM highlight_annotation;")
