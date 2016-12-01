import csv
import psycopg2
import uuid
import datetime
from sets import Set
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

#1. pip install psycopg2

csvfiles = ['data/pkddi-katrina-latest-08152016.csv', 'data/pkddi-amy-latest-08152016.csv']

DATABASE = 'mpevidence'

if len(sys.argv) > 5:
	HOSTNAME = str(sys.argv[1])
	PORT = str(sys.argv[2])
	USERNAME = str(sys.argv[3])
	PASSWORD = str(sys.argv[4])
	isClean = str(sys.argv[5])
else:
	print "Usage: loadDomeoAnnsToRDB.py <pg hostname> <pg port> <pg username> <pg password> <clean existing data (1: yes, 0: no)>"
	sys.exit(1)


def connect_postgreSQL():

	myConnection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)	
	print("Postgres connection created")
	return myConnection


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

	qry2 = "INSERT INTO highlight_annotation (urn, type, has_body, has_target, creator, date_created, date_updated) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (urn, "all", str(has_body), str(has_target), creator, date_created, date_updated);
	cur.execute(qry2);

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
	subjectDrug = row["subject"]; objectDrug = row["object"]; source = row["source"].replace("dbmi-icode-01.dbmi.pitt.edu:80","localhost")
	#print source + "| " + subjectDrug + " | " + objectDrug	

	if source in highlightD:
		highlightD[source].add(subjectDrug)
		highlightD[source].add(objectDrug)
	else:
		highlightD[source] = Set([subjectDrug, objectDrug])


def truncateall(conn):
	cur = conn.cursor()
	cur.execute("DROP TABLE qualifier;")
	cur.execute("DROP TABLE oa_claim_body;")
	cur.execute("DROP TABLE oa_selector;")
	cur.execute("DROP TABLE oa_target;")
	cur.execute("DROP TABLE data_field;")
	cur.execute("DROP TABLE oa_data_body;")
	cur.execute("DROP TABLE mp_data_annotation;")
	cur.execute("DROP TABLE material_field;")
	cur.execute("DROP TABLE oa_material_body;")
	cur.execute("DROP TABLE mp_material_annotation;")
	cur.execute("DROP TABLE method;")
	cur.execute("DROP TABLE claim_reference_relationship;")
	cur.execute("DROP TABLE mp_reference;")
	cur.execute("DROP TABLE mp_claim_annotation;")
	cur.execute("DROP TABLE highlight_annotation;")
	cur.execute("DROP TABLE oa_highlight_body;")

	cur.execute("DROP SEQUENCE mp_claim_annotation_id_seq;")
	cur.execute("DROP SEQUENCE oa_selector_id_seq;")
	cur.execute("DROP SEQUENCE oa_target_id_seq;")
	cur.execute("DROP SEQUENCE oa_claim_body_id_seq;")
	cur.execute("DROP SEQUENCE qualifier_id_seq;")
	cur.execute("DROP SEQUENCE mp_data_annotation_id_seq;")
	cur.execute("DROP SEQUENCE oa_data_body_id_seq;")
	cur.execute("DROP SEQUENCE data_field_id_seq;")
	cur.execute("DROP SEQUENCE mp_material_annotation_id_seq;")
	cur.execute("DROP SEQUENCE oa_material_body_id_seq;")
	cur.execute("DROP SEQUENCE material_field_id_seq;")
	cur.execute("DROP SEQUENCE method_id_seq;")
	cur.execute("DROP SEQUENCE claim_reference_relationship_id_seq;")
	cur.execute("DROP SEQUENCE mp_reference_id_seq;")
	cur.execute("DROP SEQUENCE highlight_annotation_id_seq;")
	cur.execute("DROP SEQUENCE oa_highlight_body_id_seq;")

def clearall(conn):
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
	cur.execute("DELETE FROM method;")
	cur.execute("DELETE FROM mp_claim_annotation;")

	cur.execute("DELETE FROM oa_highlight_body;")
	cur.execute("DELETE FROM highlight_annotation;")

	#cur.execute("ALTER TABLE mp_data_annotation ADD CONSTRAINT mp_data_annotation_mp_claim_id_fkey FOREIGN KEY (mp_claim_id) REFERENCES mp_claim_annotation (id)")


def show_table(conn, table):
	cur = conn.cursor()
	cur.execute("SELECT * FROM " + table)
	for row in cur.fetchall():
		print(row)


# load table "method" one row
def load_method(conn, row, mp_claim_id):
	cur = conn.cursor()
	cur.execute("INSERT INTO method (value, mp_claim_id, mp_data_index)" +
				"VALUES ( '" + row['assertionType'] + "', " + str(mp_claim_id) + ", 1);")


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


# load table "oa_claim_body" one row
# return claim body id
def load_oa_claim_body(conn, subject, predicate, object, exact):
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	label = subject + "_" + predicate + "_" + object
	
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
	cur.execute("INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, concept_code, vocabulary_id, qvalue)" +
				"VALUES ( '" + uuid.uuid4().hex + "', " + str(claim_body_id) + ", true, false, false, NULL, NULL, '" + row['subject'] + "')," +
				"( '" + uuid.uuid4().hex + "', " + str(claim_body_id) + ", false, true, false, NULL, NULL, '" + row['predicate'] + "')," +
				"( '" + uuid.uuid4().hex + "', " + str(claim_body_id) + ", false, false, true, NULL, NULL, '" + row['object'] + "');")


# load table "mp_claim_annotation" one row
# return claim annotation id
def load_mp_claim_annotation(conn, date, has_body, has_target, creator):
	cur = conn.cursor()
	urn = uuid.uuid4().hex

	qry1 = "INSERT INTO mp_claim_annotation (urn, has_body, has_target, creator, date_created, date_updated)" + "VALUES ('%s','%s','%s','%s','%s','%s');" % (urn, str(has_body), str(has_target), creator, parse_date(date), parse_date(date))
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
	ev_supports = 'false'
	if 'supports' in row['evidenceType']:
		ev_supports = 'true'
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO mp_data_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created)" +
				"VALUES ( '" + urn + "', '" + data_type + "', " + str(has_target) + ", '" + creator + "', " +
				str(mp_claim_id) + ", 1, " + ev_supports + ", '" + parse_date(row['date']) + "');")
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
	value = data_type
	ttype = data_type + "Type"
	direction = data_type + "Direction"

	cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number)" +
				"VALUES ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'value', '" + row[value] + "', NULL)," +
				"( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'type', '" + row[ttype] + "', NULL)," +
				"( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'direction', '" + row[direction] + "', NULL);")


# load table "mp_material_annotation" and "oa_material_body" one row
def load_mp_material_annotation(conn, row, mp_claim_id, has_target, creator):
	cur = conn.cursor()

	if (row['objectDose'] != '') and (row['objectDose'].lower() != 'unk'):
		material_body_id = helper_load_material(conn, row, mp_claim_id, has_target, creator, 'object_dose')
		load_material_field(conn, row, material_body_id, 'object')

	if (row['subjectDose'] != '') and (row['subjectDose'].lower() != 'unk'):
		material_body_id = helper_load_material(conn, row, mp_claim_id, has_target, creator, 'subject_dose')
		load_material_field(conn, row, material_body_id, 'precipt')

	if (row['numOfParticipants'] != '') and (row['numOfParticipants'].lower() != 'unk'):
		material_body_id = helper_load_material(conn, row, mp_claim_id, has_target, creator, 'participants')
		load_material_field(conn, row, material_body_id, 'participants')


def helper_load_material(conn, row, mp_claim_id, has_target, creator, data_type):
	ev_supports = 'false'
	if 'supports' in row['evidenceType']:
		ev_supports = 'true'
	cur = conn.cursor()
	urn = uuid.uuid4().hex
	cur.execute("INSERT INTO mp_material_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created)" +
				"VALUES ( '" + urn + "', '" + data_type + "', " + str(has_target) + ", '" + creator + "', " +
				str(mp_claim_id) + ", 1, " + ev_supports + ", '" + parse_date(row['date']) + "');")
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
		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
					"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'participants', NULL, " + row['numOfParticipants'] + ");")
	else:
		value = material_type + "Dose"
		regimens = material_type + "Regimens"
		formulation = material_type + "Formulation"
		duration = material_type + "Duration"
		if material_type == "precipt":
			value = "subjectDose"

		cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
					"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'value', '" + row[value] + "', NULL);")

		if (row[regimens] != '') and (row[regimens].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'regimens', '" + row[regimens] + "', NULL);")
		if (row[formulation] != '') and (row[formulation].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'formulation', '" + row[formulation] + "', NULL);")
		if (row[duration] != '') and (row[duration].lower() != 'unk'):
			cur.execute("INSERT INTO material_field (urn, material_body_id, material_field_type, value_as_string, value_as_number)" +
						"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'duration', '" + row[duration] + "', NULL);")


def parse_date(csv_date):
	temp = csv_date.replace(' -0400', '');
	return temp


#   add column: predicate, subject, object, subjectDose, objectDose
def preprocess(csvfile):
	csv_columns = ['source', 'date', 'assertionType', 'evidenceType', 'prefix', 'exactText', 'suffix',
				   'modality', 'statementType', 'comment', 'drug1Lab', 'drug1Type', 'drug1Role', 'dose1',
				   'drug2Lab', 'drug2Type', 'drug2Role', 'dose2', 'objectRegimens', 'objectFormulation',
				   'objectDuration', 'preciptRegimens', 'preciptFormulation', 'preciptDuration',
				   'numOfParticipants', 'auc', 'aucType', 'aucDirection', 'clearance', 'clearanceType', 'clearanceDirection',
				   'cmax', 'cmaxType', 'cmaxDirection', 'halflife', 'halflifeType', 'halflifeDirection', 'predicate',
				   'subject', 'object', 'subjectDose', 'objectDose']
	writer = csv.DictWriter(open('data/preprocess-domeo.csv', 'w'), fieldnames=csv_columns)
	writer.writeheader()
	reader = csv.DictReader(utf_8_encoder(open(csvfile, 'r')))
	all = []
	for row in reader:
		#print(row)

		# translate Domeo old form for dose (tablet -> Oral)
		if row['objectFormulation'] == "tablet":
			row['objectFormulation'] = "Oral"
		if row['preciptFormulation'] == "tablet":
			row['preciptFormulation'] = "Oral"

		row.update({'predicate': 'interact_with'})
		if 'object' in row['drug1Role']:
			row.update({'subject': row['drug2Lab'], 'object': row['drug1Lab'], 'subjectDose': row['dose2'], 'objectDose': row['dose1']})
		else:
			row.update({'subject': row['drug1Lab'], 'object': row['drug2Lab'], 'subjectDose': row['dose1'], 'objectDose': row['dose2']})

		if "'" in row['prefix']:
			row['prefix'] = row['prefix'].replace("'", "''")
		if "'" in row['exactText']:
			row['exactText'] = row['exactText'].replace("'", "''")
		if "'" in row['suffix']:
			row['suffix'] = row['suffix'].replace("'", "''")
		all.append(row)
	writer.writerows(all)


def load_data_from_csv(conn, reader, creator):

	highlightD = {} # drug highlight set in documents {"doc url" : "drug set"}

	for row in reader:

		prefix = row["prefix"]; exact = row["exactText"]; suffix = row["suffix"]
		source = row["source"]; date = row["date"]
		subject = row["subject"]; predicate = row["predicate"]; object = row["object"]
		oa_selector_id = load_oa_selector(conn, prefix, exact, suffix)
		oa_target_id = load_oa_target(conn, source, oa_selector_id)
		oa_claim_body_id = load_oa_claim_body(conn, subject, predicate, object, exact)
		load_qualifier(conn, row, oa_claim_body_id)
		mp_claim_id = load_mp_claim_annotation(conn, date, oa_claim_body_id, oa_target_id, creator)

		update_oa_claim_body(conn, mp_claim_id, oa_claim_body_id)
		load_mp_data_annotation(conn, row, mp_claim_id, oa_target_id, creator)
		load_mp_material_annotation(conn, row, mp_claim_id, oa_target_id, creator)
		load_method(conn, row, mp_claim_id)

		generateHighlightSet(row, highlightD)   # add unique drugs to set
		
	load_highlight(conn, highlightD)  # load drug highlight annotation

	conn.commit()

def main():

	print("[INFO] connect postgreSQL ...")
	conn = connect_postgreSQL()

	if isClean == "1":
		print("[INFO] begin clean before load ...")
		clearall(conn)
		# truncateall(conn) # don't need delete tables
		conn.commit()
		print("[INFO] clean data done ...")
	
	print("[INFO] begin load data ...")
	for csvfile in csvfiles:
		preprocess(csvfile)
		reader = csv.DictReader(utf_8_encoder(open('data/preprocess-domeo.csv', 'r')))
		creator = csvfile.split('-')[1]
		load_data_from_csv(conn, reader, creator)

	conn.close()
	print("[INFO] load completed ...")


if __name__ == '__main__':
	main()


