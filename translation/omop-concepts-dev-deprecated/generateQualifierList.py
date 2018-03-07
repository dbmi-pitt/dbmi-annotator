import psycopg2


PG_HOST = "localhost"
PG_USER = "dbmiannotator"
PG_PASSWORD = ""
PG_DATABASE = "mpevidence"

def run (hostname, username, password, database):
	resD = {}
	
	conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)	
	cur = conn.cursor()
	cur.execute("set schema 'ohdsi';")
	cur.execute("select distinct q.qvalue as drug, t.has_source as source, s.exact as sentence from qualifier q join mp_claim_annotation cann on q.claim_body_id = cann.has_body left join oa_target t on cann.has_target = t.id left join oa_selector s on t.has_selector = s.id where q.subject = True or q.object = True;")

	for row in cur.fetchall():
		drugname = row[0].replace(".",""); source = row[1]; text = row[2]
		if drugname not in resD:
			resD[drugname] = {"source": source, "text": text}
	conn.close()
	return resD


if __name__ == '__main__':
	resD = run(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	drugSortedL = sorted(resD.keys())
	
	print '"name","source","text","RxNorm","MESH","PRO","NDFRT","enantiomer","metabolite","conceptId"'
	for drug in drugSortedL:
		print '"' + drug + '","' + resD[drug]["source"]+ '","' + resD[drug]["text"] + '"' 

