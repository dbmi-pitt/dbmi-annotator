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


# QUALIFIER ################################################################
def insert_qualifier(conn, qualifier, claim_body_id):
	cur = conn.cursor()

	s = qualifier.subject; p = qualifier.predicate; o = qualifier.object
	qvalue = qualifier.qvalue
	cpt_code = qualifier.concept_code; vocab_id = qualifier.vocabulary_id
	type_cpt_code = qualifier.qualifier_type_concept_code
	type_vocab_id = qualifier.qualifier_type_vocabulary_id
	role_cpt_code = qualifier.qualifier_role_concept_code
	role_vocab_id = qualifier.qualifier_role_vocabulary_id
	enantiomer = qualifier.enantiomer
	metabolite = qualifier.metabolite

	cur.execute("INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, qvalue, concept_code, vocabulary_id, qualifier_type_concept_code, qualifier_type_vocabulary_id, qualifier_role_concept_code, qualifier_role_vocabulary_id, enantiomer, metabolite) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (uuid.uuid4().hex, claim_body_id, s, p, o, qvalue, cpt_code, vocab_id, type_cpt_code, type_vocab_id, role_cpt_code, role_vocab_id, enantiomer, metabolite))


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

# MP CLAIM ##########################################################################
# insert to table "mp_claim_annotation" 
# return claim annotation id
def insert_claim_annotation(conn, annotation, oa_claim_body_id, claim_target_id, negation):
	curr_date = datetime.datetime.now()
	creator = annotation.creator; urn = annotation.urn
	rejected = annotation.rejected_statement; rejected_reason = annotation.rejected_statement_reason; rejected_comment = annotation.rejected_statement_comment

	cur = conn.cursor()
	cur.execute("INSERT INTO mp_claim_annotation (urn, has_body, has_target, creator, date_created, date_updated, negation, rejected_statement, rejected_statement_reason, rejected_statement_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (urn, oa_claim_body_id, claim_target_id, creator, curr_date, curr_date, negation, rejected, rejected_reason, rejected_comment))

	cur.execute("SELECT * FROM mp_claim_annotation WHERE urn = '" + urn + "';")

	for row in cur.fetchall():
		return row[0]
	return None


# load table "oa_claim_body" one row
# return claim body id
def insert_claim_body(conn, claimlabel, exact):
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	
	qry1 = "INSERT INTO oa_claim_body (urn, label, claim_text) VALUES ('%s', '%s', '%s');" % (urn, claimlabel, exact)
	cur.execute(qry1)

	qry2 = "SELECT * FROM oa_claim_body WHERE urn = '%s';" % (urn)
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None

def update_claim_body(conn, is_oa_body_of, oa_claim_body_id):
	cur = conn.cursor()
	cur.execute("UPDATE oa_claim_body SET is_oa_body_of = " + str(is_oa_body_of) +
				" WHERE id = " + str(oa_claim_body_id) + ";")


# MP MATERIAL #######################################################################
def insert_material_annotation(conn, mp_claim_id, target_id, creator, material_type, mp_data_index, ev_supports):
	cur = conn.cursor()
	curr_date = datetime.datetime.now(); urn = uuid.uuid4().hex

	cur.execute("INSERT INTO mp_material_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", (urn, material_type, target_id, creator, mp_claim_id, mp_data_index, ev_supports, curr_date))

	cur.execute("SELECT * FROM mp_material_annotation WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		material_annotation_id = result[0]

	material_body_id = insert_material_body(conn, material_type, material_annotation_id)
	cur.execute("UPDATE mp_material_annotation SET has_body = "+str(material_body_id)+" WHERE id = " + str(material_annotation_id) + ";")

	return material_body_id

def insert_material_body(conn, material_type, material_annotation_id):
	urn = uuid.uuid4().hex
	cur = conn.cursor()
	cur.execute("INSERT INTO oa_material_body (urn, material_type, is_oa_body_of) VALUES (%s, %s, %s);", (urn, material_type, material_annotation_id))
	cur.execute("SELECT * FROM oa_material_body WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		material_body_id = result[0]

	return material_body_id


# load table "material_field" one row
def insert_material_field(conn, material_body_id, material_field_type, value_as_string, value_as_number, value_as_concept_id):

	cur = conn.cursor()
	cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number, value_as_concept_id) VALUES (%s, %s, %s, %s, %s, %s);", (uuid.uuid4().hex, material_body_id, material_field_type, value_as_string, value_as_number, value_as_concept_id))


# # MP DATA #########################################################################
def insert_data_annotation(conn, mp_claim_id, has_target, creator, data_type, mp_data_index, ev_supports):

	cur = conn.cursor(); urn = str(uuid.uuid4().hex)
	cur.execute("""INSERT INTO mp_data_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created, rejected, rejected_reason, rejected_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",(urn ,data_type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, curr_date, None, None, None))

	cur.execute("SELECT * FROM mp_data_annotation WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		data_annotation_id = result[0]
	
	oa_data_body_id = insert_data_body(conn, data_type, data_annotation_id)

	cur.execute("UPDATE mp_data_annotation SET has_body = " + str(oa_data_body_id) +
				" WHERE id = " + str(data_annotation_id) + ";")
	return oa_data_body_id


def insert_data_body(conn, data_type, data_annotation_id):
	cur = conn.cursor()

	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO oa_data_body (urn, data_type, is_oa_body_of) VALUES (%s, %s, %s);", (urn, data_type, data_annotation_id))
	cur.execute("SELECT * FROM oa_data_body WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		oa_data_body_id = result[0]
	return oa_data_body_id


def insert_data_field(conn, data_body_id, data_field_type, value_as_string, value_as_number, value_as_concept_id):

	cur = conn.cursor()
	cur.execute("""INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number, value_as_concept_id) VALUES (%s, %s, %s, %s, %s, %s)""", (uuid.uuid4().hex, data_body_id, data_field_type, value_as_string, value_as_number, value_as_concept_id))


# # HIGHLIGHT ANNOTATION ########################################################
# def insert_highlight_annotation(conn, type, has_body, has_target, creator, date_created, date_updated):
# 	urn = uuid.uuid4().hex
# 	cur = conn.cursor()

# 	qry2 = "INSERT INTO highlight_annotation (urn, type, has_body, has_target, creator, date_created, date_updated) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (urn, "all", str(has_body), str(has_target), creator, date_created, date_updated);
# 	cur.execute(qry2);

# 	qry2 = "SELECT * FROM highlight_annotation WHERE urn = '%s';" % (urn)
# 	cur.execute(qry2)
# 	for row in cur.fetchall():
# 		return row[0]
# 	return None


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
def insert_method(conn, enteredVal, inferredVal, mp_claim_id, mp_data_index):
	cur = conn.cursor()
	cur.execute("INSERT INTO method (entered_value, inferred_value, mp_claim_id, mp_data_index) VALUES (%s, %s, %s, %s);", (enteredVal, inferredVal, mp_claim_id, mp_data_index))

	cur.execute("SELECT id from method WHERE mp_claim_id = %s and mp_data_index = %s", (mp_claim_id, mp_data_index))

	for row in cur.fetchall():
		return row[0]
	return None

def insert_evidence_question(conn, question, value, method_id):
	cur = conn.cursor()
	cur.execute("INSERT INTO evidence_question (method_id, question, value_as_string) VALUES (%s, %s, %s);", (method_id, question, value))


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
	cur.execute("DROP TABLE IF EXISTS evidence_question;")
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
	cur.execute("DROP SEQUENCE IF EXISTS evidence_question_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS method_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS claim_reference_relationship_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS mp_reference_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS highlight_annotation_id_seq;")
	cur.execute("DROP SEQUENCE IF EXISTS oa_highlight_body_id_seq;")

def clearAll(conn):
	cur = conn.cursor()
	#cur.execute("ALTER TABLE mp_data_annotation DROP CONSTRAINT mp_data_annotation_mp_claim_id_fkey")
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
	cur.execute("DELETE FROM evidence_question;")
	cur.execute("DELETE FROM method;")
	cur.execute("DELETE FROM mp_claim_annotation;")
	cur.execute("DELETE FROM oa_highlight_body;")
	cur.execute("DELETE FROM highlight_annotation;")
