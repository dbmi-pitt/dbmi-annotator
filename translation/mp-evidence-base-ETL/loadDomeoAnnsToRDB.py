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
import psycopg2
import uuid, os
import datetime
from sets import Set
import sys  
from postgres import connection as pgconn
from postgres import mpEvidenceLoad as pgmp
from validate import validateResults

reload(sys)  
sys.setdefaultencoding('utf8')


#1. pip install psycopg2

SPLS_CSVS = ['data/pkddi-katrina-latest-03302017.csv', 'data/pkddi-amy-latest-03302017.csv']
PG_DATABASE = 'mpevidence'
DB_SCHEMA = "../../db-schema/mp_evidence_schema.sql"

annsDictCsv = {} ## keep document and count of annotations for validation after load
## DIDEO URIs and OMOP concept Ids 
dideoD = {"drug-product": "DIDEO_00000005", "precipitant": "DIDEO_00000013", "object": "DIDEO_00000012", "auc": "DIDEO_00000093", "cmax": "DIDEO_00000099", "clearance": "DIDEO_00000101", "halflife": "DIDEO_00000100"}
conceptD = {"drug-product": -9900002, "precipitant": -9900004, "object": -9900005, "auc": -9900006 , "cmax": -9900007, "clearance": -9900008, "halflife": -9900009}

## 67 formal sets - Dailymed product labels
formalSets = ["ac387aa0-3f04-4865-a913-db6ed6f4fdc5","513a41d0-37d4-4355-8a6d-a2c643bce6fa","2e7350bd-ab32-4619-a3f9-12fdf56fc5e2","b891bd9f-fdb8-4862-89c5-ecdd700398a3","4259d9b1-de34-43a4-85a8-41dd214e9177","13bb8267-1cab-43e5-acae-55a4d957630a","5f356c1b-96bd-4ef1-960c-91cf4905e6b1","53664f8d-3a93-9f2b-daee-380707e4062c","326e8ab0-6886-4749-9544-885b37070051","c25f968b-7037-4f60-9a02-2189769b0cbf","a9ff32c4-3bcf-4e51-ae8c-81ff0191ec35","829a4f51-c882-4b64-81f3-abfb03a52ebe","f371258d-91b3-4b6a-ac99-434a1964c3af","16a4a314-f97e-4e91-95e9-576a3773d284","4c401522-0108-49cb-8a41-fb5ad4dd0fb1","c3ca69e6-1ea0-4c2c-abcb-7264b2e79a87","010f9162-9f7f-4b6d-a6e4-4f832f26f38e","ea35caf8-c8c8-481a-97a2-25f68cbc240b","a16297df-3158-48db-85e5-5cd506885556","1809bcb4-5fcc-45ca-986a-4fa5edcd4b5e","3e593725-3fc9-458e-907d-19d51d5a7f9c","c66a11c1-3093-45ef-b348-3b196c05ba0c","75bf3473-2d70-4d41-93cd-afa1015e45bb","e17dc299-f52d-414d-ab6e-e809bd6f8acb","b8881a81-75d7-43e8-825f-37c352c146dc","0177d783-773c-41bf-9db9-eb7e5c64474a","a435da9d-f6e8-4ddc-897d-8cd2bf777b21","51ff7db5-aaf9-4c3c-86e6-958ebf16b60f","4b0700c9-b417-4c3a-b36f-de461e125bd3","43452bf8-76e7-47a9-a5d8-41fe84d061f0","7b8e5b26-b9e4-4704-921b-3c3c0d159916","49c4105b-e518-481c-a248-6684135f5bc1","036db1f2-52b3-42a0-acf9-817b7ba8c724","afad3051-9df2-4c54-9684-e8262a133af8","5429f134-839f-4ffc-9944-55f51238def8","5f0c6f5f-b906-4c8f-8580-3939a476a1c1","b074f950-246a-41f0-aedf-32f38998a4b1","d5051fbc-846b-4946-82df-341fb1216341","4e1e5249-1cb7-4cc2-ad5a-cdeeee2f494f","e86adbc4-a03e-4f43-a88c-b9015d18ff9f","b580471f-44a1-4da0-96ad-2f537eabec3e","d78e9639-6fab-4a78-8b29-6991a18ae6c6","a971ea18-40cf-4a01-b696-180ccc3fddb5","9c4bedb4-2d59-4fcd-aad7-fce988cd96d8","1a5a93be-7bc3-4714-9308-2fbfb8260e23","7d1a9689-23c8-44ef-a474-8c607e13d794","ee49f3b1-1650-47ff-9fb1-ea53fe0b92b6","827cf470-485d-4925-85f2-8933a6dea830","39a5dae2-49f7-4662-9eac-aa7b4c7807a4","2f44db39-e1d9-451e-ba31-e4b10366a430","d76d5540-7bae-4719-8166-f2a9106338df","50914a46-eab6-4c83-97cf-6ab0234c8126","2f2db2f5-49d3-4d47-a08a-628df49d2120","309f8ac3-a3fd-4313-96aa-7f21fa9cd646","a4ee3907-45d4-41b9-af8a-39a9966cd533","a0da0dba-a56d-486b-a45b-e8a7cdfbeac6","c6e131fe-e7df-4876-83f7-9156fc4e8228","aad8b373-0aec-4efb-8e61-3d8114b31127","520428f1-2cd5-447f-8782-c8505ce65b72","44dcbf97-99ec-427c-ba50-207e0069d6d2","ad386ed4-a284-4da5-b79a-3c0f4165057a","1fd0ba23-962e-427f-8b9d-2cf8f64d0f95","fdbfe194-b845-42c5-bb87-a48118bc72e7","d2f6d2d0-1b32-4caf-9fce-6b798c94204b","ba74e3cd-b06f-4145-b284-5fd6b84ff3c9","e9481622-7cc6-418a-acb6-c5450daae9b0","10db92f9-2300-4a80-836b-673e1ae91610"]


if len(sys.argv) > 5:
	PG_HOST = str(sys.argv[1])
	PG_PORT = str(sys.argv[2])
	PG_USER = str(sys.argv[3])
	PG_PASSWORD = str(sys.argv[4])
	isClean = str(sys.argv[5])
else:
	print "Usage: loadDomeoAnnsToRDB.py <pg hostname> <pg port> <pg username> <pg password> <OPTIONS (1: clean all tables, 2 drop and recreate all tables, 0: keep existing data)>"
	sys.exit(1)


def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')


def load_highlight(conn, highlightD):

	currentTime = datetime.datetime.now()

	for url, drugS in highlightD.iteritems():
		for drug in drugS:
			oa_selector_id = load_oa_selector(conn, "", drug, "")
			oa_target_id = load_oa_target(conn, url, oa_selector_id)
			oa_highlight_body_id = load_oa_highlight_body(conn, drug, url)
			highlight_annotation_id = load_highlight_annotation(conn, type, oa_highlight_body_id, oa_target_id, "Domeo", currentTime, currentTime)
			update_oa_highlight_body(conn, highlight_annotation_id, oa_highlight_body_id)


def load_highlight_annotation(conn, type, has_body, has_target, creator, date_created, date_updated):
	urn = uuid.uuid4().hex
	cur = conn.cursor()

	cur.execute("INSERT INTO highlight_annotation (urn, type, has_body, has_target, creator, date_created, date_updated, article_highlight, mp_claim_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (urn, "all", str(has_body), str(has_target), creator, date_created, date_updated, True, None));

	qry2 = "SELECT * FROM highlight_annotation WHERE urn = '%s';" % (urn)
	cur.execute(qry2)
	for row in cur.fetchall():
		return row[0]
	return None

def load_oa_highlight_body(conn, drug, url):
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
	preciptDrug = row["precipt"]; objectDrug = row["object"]; source = row["source"].replace("dbmi-icode-01.dbmi.pitt.edu:80","localhost")

	if source in highlightD:
		highlightD[source].add(preciptDrug)
		highlightD[source].add(objectDrug)
	else:
		highlightD[source] = Set([preciptDrug, objectDrug])


# load table "method" one row
def load_method(conn, row, mp_claim_id):
	cur = conn.cursor()

	enteredVal = row["assertionType"]
		
	cur.execute("INSERT INTO method (entered_value, inferred_value, mp_claim_id, mp_data_index) VALUES (%s, %s, %s, %s);", (enteredVal, None, str(mp_claim_id), 1))

# When dose 1 and dose2 available and one of in auc, cmax, clearance, halflife available then return True, else return False
def isClinicalTrial(row):
	if ((row["dose1"] and row["dose1"].lower() != "unk") or (row["dose2"] and row["dose2"].lower() != "unk")) and ((row["auc"] and row["auc"].lower() != "unk") or (row["cmax"] and row["cmax"].lower() != "unk") or (row["clearance"] and row["clearance"].lower() != "unk") or (row["halflife"] and row["halflife"].lower() != "unk")):
		return True
	else:
		return False
	

# load table "oa_selector" one row
# input: conn, prefix, exact, suffix
# return: selector id
def load_oa_selector(conn, prefix, exact, suffix):
	cur = conn.cursor()
	urn = uuid.uuid4().hex

	cur.execute("SET SCHEMA 'ohdsi';")
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


# load table "oa_claim_body" one row
# return claim body id
def load_oa_claim_body(conn, precipt, predicate, object, exact):
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	label = precipt + "_" + predicate + "_" + object
	
	qry1 = "INSERT INTO oa_claim_body (urn, label, claim_text) VALUES ('%s', '%s', '%s');" % (urn, label, exact)
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


# load table "qualifier" one row
def load_qualifier(conn, row, claim_body_id):
	cur = conn.cursor()

	cur.execute("""INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, qvalue, concept_code, vocabulary_id, qualifier_type_concept_code, qualifier_type_vocabulary_id, qualifier_role_concept_code, qualifier_role_vocabulary_id, enantiomer, metabolite) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (uuid.uuid4().hex, claim_body_id, True, False, False, row['precipt'], None, None, dideoD["drug-product"], conceptD["drug-product"], dideoD["precipitant"], conceptD["precipitant"], False, False))

	cur.execute("""INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, qvalue, concept_code, vocabulary_id, qualifier_type_concept_code, qualifier_type_vocabulary_id, qualifier_role_concept_code, qualifier_role_vocabulary_id, enantiomer, metabolite) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (uuid.uuid4().hex, claim_body_id, False, True, False, row['predicate'], None, None, None, None, None, None, None, None))

	cur.execute("""INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, qvalue, concept_code, vocabulary_id, qualifier_type_concept_code, qualifier_type_vocabulary_id, qualifier_role_concept_code, qualifier_role_vocabulary_id, enantiomer, metabolite) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (uuid.uuid4().hex, claim_body_id, False, False, True, row['object'], None, None, dideoD["drug-product"], conceptD["drug-product"], dideoD["object"], conceptD["object"], False, False))


# load table "mp_claim_annotation" one row
# return claim annotation id
def load_mp_claim_annotation(conn, date, has_body, has_target, creator, negation):
	cur = conn.cursor()
	urn = uuid.uuid4().hex

	qry1 = "INSERT INTO mp_claim_annotation (urn, has_body, has_target, creator, date_created, date_updated, negation) VALUES ('%s','%s','%s','%s','%s','%s','%s');" % (urn, str(has_body), str(has_target), creator, parse_date(date), parse_date(date), negation)
	cur.execute(qry1)

	cur.execute("SELECT * FROM mp_claim_annotation WHERE urn = '" + urn + "';")

	for row in cur.fetchall():
		return row[0]
	return None


# load table "mp_data_annotation" and "oa_data_body" one row
def load_mp_data_annotation(conn, row, mp_claim_id, has_target, creator):
	cur = conn.cursor()

	if (row['auc'] != '') and (row['auc'].lower() != 'unk'):
		data_body_id = helper_load_data(conn, row, mp_claim_id, has_target, creator, 'auc')
		load_data_field(conn, row, data_body_id, 'auc')

	if (row['cmax'] != '') and (row['cmax'].lower() != 'unk'):
		data_body_id = helper_load_data(conn, row, mp_claim_id, has_target, creator, 'cmax')
		load_data_field(conn, row, data_body_id, 'cmax')

	if (row['clearance'] != '') and (row['clearance'].lower() != 'unk'):
		data_body_id = helper_load_data(conn, row, mp_claim_id, has_target, creator, 'clearance')
		load_data_field(conn, row, data_body_id, 'clearance')

	if (row['halflife'] != '') and (row['halflife'].lower() != 'unk'):
		data_body_id = helper_load_data(conn, row, mp_claim_id, has_target, creator, 'halflife')
		load_data_field(conn, row, data_body_id, 'halflife')


def helper_load_data(conn, row, mp_claim_id, has_target, creator, data_type):

	ev_supports = getEvRelationship(row["modality"], row["evidenceType"])
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO mp_data_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", (urn, data_type, str(has_target), creator, str(mp_claim_id), 1, ev_supports, parse_date(row['date'])))

	cur.execute("SELECT * FROM mp_data_annotation WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		data_annotation_id = result[0]
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO oa_data_body (urn, data_type, is_oa_body_of, vocabulary_id, concept_code) VALUES (%s, %s, %s, %s, %s);", (urn, data_type, data_annotation_id, conceptD[data_type], dideoD[data_type]))
	cur.execute("SELECT * FROM oa_data_body WHERE urn = '" + urn + "';")
	for result in cur.fetchall():
		has_body = result[0]
	cur.execute("UPDATE mp_data_annotation SET has_body = " + str(has_body) +
				" WHERE id = " + str(data_annotation_id) + ";")
	return has_body


# load table "data_field" one row
def load_data_field(conn, row, data_body_id, data_type):
	cur = conn.cursor()
	value = data_type
	ttype = data_type + "Type"
	direction = data_type + "Direction"

	cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);",(uuid.uuid4().hex, str(data_body_id), 'value', row[value], None))
	cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);",(uuid.uuid4().hex, str(data_body_id), 'type', row[ttype], None))
	cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);",(uuid.uuid4().hex, str(data_body_id), 'direction', row[direction], None))


# load table "mp_material_annotation" and "oa_material_body" one row
# precipt as subject
def load_mp_material_annotation(conn, row, mp_claim_id, has_target, creator):
	cur = conn.cursor()

	if (row['preciptDose'] != ''):
		material_body_id = helper_load_material(conn, row, mp_claim_id, has_target, creator, 'precipitant_dose')
		load_material_field(conn, row, material_body_id, 'precipitant_dose', 'precipt')

	if (row['objectDose'] != ''):
		material_body_id = helper_load_material(conn, row, mp_claim_id, has_target, creator, 'object_dose')
		load_material_field(conn, row, material_body_id, 'object_dose', 'object')

	if (row['numOfParticipants'] != '' and row['numOfParticipants'].lower() != "unk"):
		material_body_id = helper_load_material(conn, row, mp_claim_id, has_target, creator, 'participants')
		load_material_field(conn, row, material_body_id, 'participants', 'participants')


def helper_load_material(conn, row, mp_claim_id, has_target, creator, data_type):

	ev_supports = getEvRelationship(row["modality"], row["evidenceType"])

	cur = conn.cursor()
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO mp_material_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", (urn, data_type, str(has_target), creator, str(mp_claim_id), 1, ev_supports, parse_date(row['date'])))

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
# material_type is participants, precipt and object
def load_material_field(conn, row, material_body_id, material_type, material_header):
	cur = conn.cursor()

	if material_type == "participants":
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);", (uuid.uuid4().hex, str(material_body_id), 'participants', None, row['numOfParticipants']))

	## load precipt dose and object dose
	elif material_type in ["precipitant_dose","object_dose"] and material_header in ["precipt", "object"]:
		value = material_header + "Dose"
		regimens = material_header + "Regimens"
		formulation = material_header + "Formulation"
		duration = material_header + "Duration"

		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);", (uuid.uuid4().hex, str(material_body_id), 'drugname', row[material_header], None))
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);", (uuid.uuid4().hex, str(material_body_id), 'value', row[value], None))

		if (row[regimens] != ''):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);", (uuid.uuid4().hex, str(material_body_id), 'regimens', row[regimens], None))

		if (row[formulation] != ''):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);", (uuid.uuid4().hex, str(material_body_id), 'formulation', row[formulation], None))

		if (row[duration] != ''):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number) VALUES (%s, %s, %s, %s, %s);", (uuid.uuid4().hex, str(material_body_id), 'duration', row[duration], None))
	else:
		print "[ERROR] load_material_field, material type (%s) or material_header (%s) undefined" % (material_type, material_header)


def parse_date(csv_date):
	temp = csv_date.replace(' -0400', '');
	return temp


#   add column: predicate, subject, object, subjectDose, objectDose
def preprocess(inputs, output):

	if os.path.exists(output):
		os.remove(output)		
		
	csv_columns = ['source', 'date', 'assertionType', 'evidenceType', 'prefix', 'exactText', 'suffix', 'modality', 'statementType', 'comment', 'drug1Lab', 'drug1Type', 'drug1Role', 'dose1', 'drug2Lab', 'drug2Type', 'drug2Role', 'dose2', 'objectRegimens', 'objectFormulation', 'objectDuration', 'preciptRegimens', 'preciptFormulation', 'preciptDuration', 'numOfParticipants', 'auc', 'aucType', 'aucDirection', 'clearance', 'clearanceType', 'clearanceDirection', 'cmax', 'cmaxType', 'cmaxDirection', 'halflife', 'halflifeType', 'halflifeDirection', 'predicate', 'precipt', 'object', 'preciptDose', 'objectDose']
	writer = csv.DictWriter(open(output, 'a'), fieldnames=csv_columns)
	writer.writeheader()

	allRows = []

	for csvfile in inputs:
		reader = csv.DictReader(utf_8_encoder(open(csvfile, 'r')))
		next(reader, None) # skip the header
		for row in reader:			
			row['source'] = row['source'].replace("dbmi-icode-01.dbmi.pitt.edu:80","localhost")
			if row['source'].replace("http://localhost/DDI-labels/","").replace(".html","") not in formalSets: # skip annotations out of 67 formal labels
				continue
			if "delete" in row['comment'].lower(): # skip deleted annotations
				print "[INFO] Skiped annotation commented as: %s" % row['comment']
				continue

			# update method
			if isClinicalTrial(row):
				row.update({'assertionType': 'DDI clinical trial'})
			else:
				row.update({'assertionType': 'Statement'})

			# translate Domeo old form for dose (tablet -> Oral)
			if row['objectFormulation'] == "tablet":
				row['objectFormulation'] = "Oral"
			if row['preciptFormulation'] == "tablet":
				row['preciptFormulation'] = "Oral"

			# all SPLs annotation's method is interact_with
			row.update({'predicate': 'interact with'})

			# make assertion in  subject (precipt) predicate object
			if 'object' in row['drug1Role'] and 'precipitant' in row['drug2Role']:
				row.update({'precipt': row['drug2Lab'], 'object': row['drug1Lab'], 'preciptDose': row['dose2'], 'objectDose': row['dose1']})
			elif 'precipitant' in row['drug1Role'] and 'object' in row['drug2Role']:
				row.update({'precipt': row['drug1Lab'], 'object': row['drug2Lab'], 'preciptDose': row['dose1'], 'objectDose': row['dose2']})
			else:
				print "[ERROR] drug role information not available: document (%s), drug1 (%s) - drug2(%s)" % (row['source'], row['drug1Lab'], row['drug2Lab'])

			if "'" in row['prefix']:
				row['prefix'] = row['prefix'].replace("'", "''")
			if "'" in row['exactText']:
				row['exactText'] = row['exactText'].replace("'", "''")
			if "'" in row['suffix']:
				row['suffix'] = row['suffix'].replace("'", "''")

			allRows.append(row)
			addAnnsToCount(annsDictCsv, row['source'])

	writer.writerows(allRows)

def addAnnsToCount(annsDict, document):
	if document in annsDict:
		annsDict[document] += 1
	else:
		annsDict[document] = 1

def getEvRelationship(modality, evidenceType):
	if ("supports" in evidenceType and "positive" in modality) or ("challenges" in evidenceType and "negative" in modality):
		return True
	elif ("supports" in evidenceType and "negative" in modality) or ("challenges" in evidenceType and "positive" in modality):
		return False
	else:
		print "[ERROR] getEvRelationship modality (%s), evidenceType (%s)" % (modality, evidenceType)
		sys.exit(0)

def getNegationForStatement(modality, evidenceType):
	if ("supports" in evidenceType and "positive" in modality) or ("challenges" in evidenceType and "negative" in modality):
		return False
	elif ("supports" in evidenceType and "negative" in modality) or ("challenges" in evidenceType and "positive" in modality):
		return True
	else:
		print "[ERROR] getNegationForStatement (%s)" % (modality, evidenceType)
		sys.exit(0)


def load_data_from_csv(conn, reader, creator):

	highlightD = {} # drug highlight set in documents {"doc url" : "drug set"}

	for row in reader:
		prefix = row["prefix"]; exact = row["exactText"]; suffix = row["suffix"]
		source = row["source"]; date = row["date"]
		subject = row["precipt"]; predicate = row["predicate"]; object = row["object"]

		# when method is statement, translate negation from Domeo SPLs annotation
		if row["assertionType"] == "Statement":
			negation = getNegationForStatement(row["modality"], row["evidenceType"])	
		# when method is clinicaltrial, evidence relationship supports/refutes
		elif row["assertionType"] == "DDI clinical trial":
			negation = False		
				
		oa_selector_id = load_oa_selector(conn, prefix, exact, suffix)
		oa_target_id = load_oa_target(conn, source, oa_selector_id)
		oa_claim_body_id = load_oa_claim_body(conn, subject, predicate, object, exact)
		load_qualifier(conn, row, oa_claim_body_id)

		mp_claim_id = load_mp_claim_annotation(conn, date, oa_claim_body_id, oa_target_id, creator, negation)

		update_oa_claim_body(conn, mp_claim_id, oa_claim_body_id)
		load_mp_data_annotation(conn, row, mp_claim_id, oa_target_id, creator)
		load_mp_material_annotation(conn, row, mp_claim_id, oa_target_id, creator)
		load_method(conn, row, mp_claim_id)
		generateHighlightSet(row, highlightD)   # add unique drugs to set
		
	load_highlight(conn, highlightD)  # load drug highlight annotation
	conn.commit()

def main():
	print("[INFO] connect postgreSQL ...")

	creator = "pharmacist"
	PREPROCESSED_CSV = 'data/preprocess-domeo.csv'

	conn = pgconn.connect_postgres(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	if isClean == "1":
		pgmp.clearAll(conn)
		conn.commit()
		print "[INFO] Clean all tables done!"
	elif isClean == "2":
		pgmp.truncateAll(conn) # delete all tables in DB mpevidence
		conn.commit()
		pgconn.createdb(conn, DB_SCHEMA)
		conn.commit()
		print "[INFO] Drop and recreate all tables done!"
	
	print "[INFO] begin load data ..."
	preprocess(SPLS_CSVS, PREPROCESSED_CSV)

	reader = csv.DictReader(utf_8_encoder(open(PREPROCESSED_CSV, 'r')))
	load_data_from_csv(conn, reader, creator)

	print "[INFO] annotation load completed!"

	if isClean in ["1","2"]:
		print "[INFO] Begin results validating..."
		if validateResults(conn, annsDictCsv):
			print "[INFO] all annotations are loaded successfully!"
		else:
			print "[WARN] annotations are loaded incompletely!"
	conn.close()

if __name__ == '__main__':
	main()
