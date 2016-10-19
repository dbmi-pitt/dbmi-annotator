import csv
import psycopg2
import uuid
import datetime
from sets import Set
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

#1. pip install psycopg2
#2. create/edit config file: "config/DB-config.txt"

csvfiles = ['data/mp-annotat2-10182016.tsv']
db_config_files = "config/DB-config.txt"
hostname = 'localhost'
database = 'mpevidence'
curr_date = datetime.datetime.now()

# UTILS ##########################################################################
def connect_postgreSQL(db_config_files):
	dbconfig = file = open(db_config_files)
	if dbconfig:
		for line in dbconfig:
			if "USERNAME" in line:
				username = line[(line.find("USERNAME=")+len("USERNAME=")):line.find(";")]
			elif "PASSWORD" in line:
				password = line[(line.find("PASSWORD=")+len("PASSWORD=")):line.find(";")]
		myConnection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)	
		print("Postgres connection created")
	else:
		print "Postgres configuration file is not found: " + dbconfig

	return myConnection

# add column: predicate, subject, object, subjectDose, objectDose
def preprocess(csvfile):
	csv_columns = ['document','claim label','claim text','method','relationship','drug1','drug2','precipitant','enzyme','evRelationship','participants','participants text','drug1 dose','drug1 formulation','drug1 duration','drug1 regimens','drug1 dose text','drug2 dose','drug2 formulation','drug2 duration','drug2 regimens','drug2 dose text','auc','auc type','auc direction','auc text','cmax','cmax type','cmax direction','cmax text','cl','cl type','cl direction','cl text','halflife','halflife type','halflife direction','halflife text','group randomization','id','parallel group design','predicate','subject','object','subjectDose','objectDose']

	writer = csv.DictWriter(open('data/preprocess-annotator.csv', 'w'), fieldnames=csv_columns)
	writer.writeheader()
	reader = csv.DictReader(utf_8_encoder(open(csvfile, 'r')), delimiter="\t")
	all = []
	for row in reader:
		#print(row)

		row.update({'predicate': row['relationship']})
		if row['precipitant'] == 'drug1':
			row.update({'subject': row['drug1'], 'object': row['drug2'], 'subjectDose': row['drug1 dose'], 'objectDose': row['drug2 dose']})
		elif row['precipitant'] == 'drug2':
			row.update({'subject': row['drug2'], 'object': row['drug1'], 'subjectDose': row['drug2 dose'], 'objectDose': row['drug1 dose']})

		# fix single quote in text
		if "'" in row['claim text']: 
			row['claim text'] = row['claim text'].replace("'", "''")
		if "'" in row['participants text']:
			row['participants text'] = row['participants text'].replace("'", "''")
		if "'" in row['drug1 dose text']:
			row['drug1 dose text'] = row['drug1 dose text'].replace("'", "''")
		if "'" in row['drug2 dose text']:
			row['drug2 dose text'] = row['drug2 dose text'].replace("'", "''")

		if "'" in row['auc text']:
			row['auc text'] = row['auc text'].replace("'", "''")
		if "'" in row['cmax text']:
			row['cmax text'] = row['cmax text'].replace("'", "''")
		if "'" in row['cl text']:
			row['cl text'] = row['cl text'].replace("'", "''")
		if "'" in row['halflife text']:
			row['halflife text'] = row['halflife text'].replace("'", "''")
		all.append(row)
	writer.writerows(all)


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def show_table(conn, table):
	cur = conn.cursor()
	cur.execute("SELECT * FROM " + table)
	for row in cur.fetchall():
		print(row)


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
		highlightD[source].add(subjectDrug.lower())
		highlightD[source].add(objectDrug.lower())
	else:
		highlightD[source] = Set([subjectDrug.lower(), objectDrug.lower()])

# CLEAN SCHEMA ################################################################
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

# load table "method" one row
def load_method(conn, row, mp_claim_id, mp_data_index):
	cur = conn.cursor()
	cur.execute("INSERT INTO method (value, mp_claim_id, mp_data_index)" +
				"VALUES ( '" + row['method'] + "', " + str(mp_claim_id) + ", "+str(mp_data_index)+");")

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


# load table "qualifier" one row
def load_qualifier(conn, subject, predicate, object, claim_body_id):
	cur = conn.cursor()
	cur.execute("INSERT INTO qualifier (urn, claim_body_id, subject, predicate, object, concept_code, vocabulary_id, qvalue)" +
				"VALUES ( '" + uuid.uuid4().hex + "', " + str(claim_body_id) + ", true, false, false, NULL, NULL, '" + subject + "')," +
				"( '" + uuid.uuid4().hex + "', " + str(claim_body_id) + ", false, true, false, NULL, NULL, '" + predicate + "')," +
				"( '" + uuid.uuid4().hex + "', " + str(claim_body_id) + ", false, false, true, NULL, NULL, '" + object + "');")

# LOAD MP MATERIAL ################################################################
# load table "mp_material_annotation" and "oa_material_body" one row
def load_mp_material_annotation(conn, row, mp_claim_id, creator, mp_data_index):
	cur = conn.cursor()
	source = row['document']

	if (row['drug1 dose'] != '') and (row['drug1 dose'].lower() != 'unk'):
		exact = row['drug1 dose text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)	
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, target_id, creator, 'object_dose', mp_data_index)
		load_material_field(conn, row, material_body_id, 'drug1')

	if (row['drug2 dose'] != '') and (row['drug2 dose'].lower() != 'unk'):
		exact = row['drug2 dose text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)	
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, target_id, creator, 'subject_dose', mp_data_index)
		load_material_field(conn, row, material_body_id, 'drug2')

	if (row['participants'] != '') and (row['participants'].lower() != 'unk'):
		exact = row['participants text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)	
		material_body_id = insert_material_annotation(conn, row, mp_claim_id, target_id, creator, 'participants', mp_data_index)
		load_material_field(conn, row, material_body_id, 'participants')


def insert_material_annotation(conn, row, mp_claim_id, has_target, creator, data_type, mp_data_index):
	ev_supports = 'false'
	if 'supports' in row['evRelationship']:
		ev_supports = 'true'

	cur = conn.cursor()
	urn = uuid.uuid4().hex
	qry1= "INSERT INTO mp_material_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');" % (urn, data_type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, curr_date)
	cur.execute(qry1)
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
					"VALUES ( '" + uuid.uuid4().hex + "', " + str(material_body_id) + ", 'participants', NULL, " + row['participants'] + ");")
	else:
		value = material_type + " dose"
		regimens = material_type + " regimens"
		formulation = material_type + " formulation"
		duration = material_type + " duration"

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


# LOAD MP DATA ################################################################
# load table "mp_data_annotation" and "oa_data_body" one row
def load_mp_data_annotation(conn, row, mp_claim_id, creator, mp_data_index):
	source = row['document']

	if (row['auc'] != '') and (row['auc'].lower() != 'unk'):
		exact = row['auc text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)		
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'auc', mp_data_index)
		load_data_field(conn, row, data_body_id, 'auc')

	if (row['cmax'] != '') and (row['cmax'].lower() != 'unk'):
		exact = row['cmax text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'cmax', mp_data_index)
		load_data_field(conn, row, data_body_id, 'cmax')

	if (row['cl'] != '') and (row['cl'].lower() != 'unk'):
		exact = row['cl text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'clearance', mp_data_index)
		load_data_field(conn, row, data_body_id, 'cl')

	if (row['halflife'] != '') and (row['halflife'].lower() != 'unk'):
		exact = row['halflife text']
		selector_id = load_oa_selector(conn, '', exact, '')
		target_id = load_oa_target(conn, source, selector_id)
		data_body_id = insert_mp_data_annotation(conn, row, mp_claim_id, target_id, creator, 'halflife', mp_data_index)
		load_data_field(conn, row, data_body_id, 'halflife')


def insert_mp_data_annotation(conn, row, mp_claim_id, has_target, creator, data_type, mp_data_index):
	ev_supports = 'false'
	if 'supports' in row['evRelationship']:
		ev_supports = 'true'

	cur = conn.cursor()
	urn = uuid.uuid4().hex
	qry1 = "INSERT INTO mp_data_annotation (urn, type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, date_created) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');" % (str(urn) ,data_type, has_target, creator, mp_claim_id, mp_data_index, ev_supports, curr_date)

	cur.execute(qry1)
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
	ttype = data_type + " type"
	direction = data_type + " direction"

	cur.execute("INSERT INTO data_field (urn, data_body_id, data_field_type, value_as_string, value_as_number)" +
				"VALUES ( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'value', '" + row[value] + "', NULL)," +
				"( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'type', '" + row[ttype] + "', NULL)," +
				"( '" + uuid.uuid4().hex + "', " + str(data_body_id) + ", 'direction', '" + row[direction] + "', NULL);")

# LOAD MP CLAIM ################################################################
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

# insert to table "mp_claim_annotation" 
# return claim annotation id
def insert_mp_claim_annotation(conn, curr_date, has_body, has_target, creator, annId):
	cur = conn.cursor()
	urn = annId

	qry1 = "INSERT INTO mp_claim_annotation (urn, has_body, has_target, creator, date_created, date_updated)" + "VALUES ('%s','%s','%s','%s','%s','%s');" % (urn, str(has_body), str(has_target), creator, curr_date, curr_date)

	cur.execute(qry1)
	cur.execute("SELECT * FROM mp_claim_annotation WHERE urn = '" + urn + "';")

	for row in cur.fetchall():
		return row[0]
	return None

def load_mp_claim_annotation(conn, row, creator):
	claimP = ""; claimE = row["claim text"]; claimS = ""
	curr_date = datetime.datetime.now()
	source = row["document"]; 
	subject = row["subject"]; predicate = row["predicate"]; object = row["object"]
	claim_selector_id = load_oa_selector(conn, claimP, claimE, claimS)
	claim_target_id = load_oa_target(conn, source, claim_selector_id)
	oa_claim_body_id = load_oa_claim_body(conn, subject, predicate, object, claimE)
	load_qualifier(conn, subject, predicate, object, oa_claim_body_id)
	
	mp_claim_id = insert_mp_claim_annotation(conn, curr_date, oa_claim_body_id, claim_target_id, creator, row['id'])
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

	print("[info] connect postgreSQL ...")
	conn = connect_postgreSQL(db_config_files)

	print("[info] clean before load ...")
	clearall(conn)
	#truncateall(conn)
	conn.commit()

	#show_table(conn, 'mp_claim_annotation') 	#show table
	
	print("[info] load data ...")
	for csvfile in csvfiles:
		preprocess(csvfile)
		reader = csv.DictReader(utf_8_encoder(open('data/preprocess-annotator.csv', 'r')))
		creator = csvfile.split('-')[1]
		load_data_from_csv(conn, reader, creator)

	conn.close()
	print("[info] load completed ...")


if __name__ == '__main__':
	main()


