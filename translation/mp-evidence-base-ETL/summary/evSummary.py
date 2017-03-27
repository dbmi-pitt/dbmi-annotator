import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from postgres import connection as pgconn

methodL = ["Statement", "DDI Clinical trial", "Phenotype clinical study", "Case Report", "Experiments"]
publisherD = {"Dailymed": "DDI-labels", "Pubmed Centre": "PMC", "Wiley": "wiley", "Elsevier": "elsevier", "Springer": "springer", "Sage": "sage", "Taylor & Francis": "taylorFrancis", "Wolters Kluwer": "wolters", "Future Medicine": "futureMedicine"}

## Get count of articles been annotated in specific method 
# "%http://localhost/wiley/wiley%", "DDI clinical trial"
def getCountByArticleMethod(conn, publisherKey, method):
	cur = conn.cursor()
	qry = """select count(distinct t.has_source)
	from mp_claim_annotation cann 
	join oa_claim_body cbody on cann.has_body = cbody.id 
	left join method met on cann.id = met.mp_claim_id 
	join oa_target t on cann.has_target = t.id
	where t.has_source like '%s'
	and met.entered_value = '%s'; """ % ('%' + publisherKey + '%', method)

	cur.execute(qry)
	for row in cur.fetchall():
		return row[0]

def printArticleAnnotatedSummary(conn):
	for label, urlkey in publisherD.iteritems():
		print "[INFO] publisher (%s) - articles been annotated ==========" % (label)
		for method in methodL:
			cnt = getCountByArticleMethod(conn, urlkey, method)
			print "  %s: %s" % (method, cnt)


def main():
	PG_HOST = "localhost"
	PG_USER = "dbmiannotator"
	PG_PASSWORD = "dbmi2016"
	PG_DATABASE = "mpevidence"

	conn = pgconn.connect_postgres(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	printArticleAnnotatedSummary(conn)

if __name__ == '__main__':
	main()
