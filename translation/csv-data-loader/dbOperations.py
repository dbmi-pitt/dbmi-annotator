import psycopg2


# DB CONNECTION ################################################################
def connect_postgreSQL(hostname, username, password, database):
	conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)	
	print("Postgres connection created")	
	return conn

# CREATE DATABASE AND TABLES ###################################################
def createdb(conn, db_schema):
	with open(db_schema) as dbscript:
		sql = dbscript.read()
		cur = conn.cursor()
		cur.execute(sql)

# DROP TABLES ################################################################
def truncateall(conn):
	cur = conn.cursor()
	cur.execute("SET SCHEMA 'ohdsi';")
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

# CLEAN ALL TABLES ################################################################
def clearall(conn):
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
