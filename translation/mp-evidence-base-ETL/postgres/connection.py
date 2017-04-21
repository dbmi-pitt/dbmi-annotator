import psycopg2

def connect_postgres(hostname, username, password, database):
	conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)	
	print("Postgres connection created")	
	return conn


def createdb(conn, db_schema):
	with open(db_schema) as dbscript:
		sql = dbscript.read()
		cur = conn.cursor()
		cur.execute(sql)


def setDbSchema(conn, name):
	cur = conn.cursor()
	cur.execute("SET SCHEMA '" + name + "';")
