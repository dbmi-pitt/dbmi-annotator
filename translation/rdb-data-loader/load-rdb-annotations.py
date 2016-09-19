import sys, csv, json
import psycopg2
import uuid
import datetime
from elasticsearch import Elasticsearch

sys.path.insert(0, './model')
from micropublication import Annotation, DataMaterialRow, DMItem, DataItem, MaterialDoseItem, MatarialParticipants

######################### VARIABLES ##########################
HOSTNAME = 'localhost'
DB_SCHEMA = 'mpevidence'
DB_CONFIG = "config/DB-config.txt"
MP_ANN_TEMPLATE = "template/mp-annotation-template.json"
ES_PORT = 9250

mpDataL = ["auc", "cmax", "cl", "t12"]

######################### QUERY ##########################
# query mp claim annotation by author name
# return claim annotation with s, p, o, source and oa selector
def queryMpClaim(conn):
	qry = """select cann.id, t.has_source, cann.creator, cann.date_created, s.exact, s.prefix, s.suffix, cbody.label, qvalue, q.subject, q.predicate, q.object 
	from mp_claim_annotation cann, oa_claim_body cbody, oa_target t, oa_selector s, qualifier q
	where cann.has_body = cbody.id
	and cann.has_target = t.id
	and t.has_selector = s.id
	and cbody.id = q.claim_body_id"""

	annotations = {} # key: id, value obj Annotation

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():
		id = row[0]
		if id not in annotations:
			annotation = Annotation()
			annotations[id] = annotation
		else:
			annotation = annotations[id]

		# claim qualifiers
		if row[9] is True:
			annotation.csubject = row[8]
		elif row[10] is True:
			annotation.cpredicate = row[8]
		elif row[11] is True:
			annotation.cobject = row[8]
		else:
			print "[ERROR] qualifier role unidentified qvalue: %s (claimid %s)" % (row[8], id) 
		# claim source and label
		if annotation.source == None:
			annotation.source = row[1]
		if annotation.label == None:
			annotation.label = row[7]

		if annotation.exact == None:
			annotation.setOaSelector(row[5], row[4], row[6])

	return annotations


# query data items for claim annotation
# return list of DataItems
def queryMpData(conn, annotation, claimid):

	qry = """	
	select dann.type, df.data_field_type, df.value_as_string, df.value_as_number, s.exact, s.prefix, s.suffix, mp_data_index
	from mp_data_annotation dann,oa_data_body dbody, data_field df, oa_target t, oa_selector s
	where dann.mp_claim_id = %s
	and dann.has_body = dbody.id
	and df.data_body_id = dbody.id
	and dann.has_target = t.id
	and t.has_selector = s.id
	""" % (claimid)

	cur = conn.cursor()
	cur.execute(qry)
	
	#print "claimid: " + str(claimid)

	for row in cur.fetchall():

		#print str(row)

		dType = row[0]  # data type
		dfType = row[1] # data field 

		value = row[2] or row[3] # value as string or number
		index = row[7] # data index
		dmRow = None

		#print dType + "," + dfType + "," + value

		if annotation.getSpecificDataMaterial(index) == None:
			dmRow = DataMaterialRow() # create new row of data & material
			dataItem = DataItem(dType)
			dataItem.setAttribute(dfType, value)
			dmRow.setDataItem(dataItem)

			#print "before: " + str(dmRow.getDataItemInRow("auc").value)
			annotation.setSpecificDataMaterial(dmRow, index)

		else: # current row of data & material exists 
			dmRow = annotation.getSpecificDataMaterial(index)

			if dmRow.getDataItemInRow(dType) != None: # current DataItem exists
				dataItem = dmRow.getDataItemInRow(dType)
				dataItem.setAttribute(dfType, value)
			else: # current DataItem not exists
				dataItem = DataItem(dType) 
				dataItem.setAttribute(dfType, value)
				dmRow.setDataItem(dataItem)

		if dmRow.getDataItemInRow("cmax") and dType == "cmax":		
			cmax = dmRow.getDataItemInRow("cmax")
			#print "before: " + str(cmax.value) + "," + str(cmax.type) + "," + str(cmax.direction)
		#annotation.setSpecificDataMaterial(dmRow, index)

	# if annotation.getSpecificDataMaterial(0) != None:
	# 	dmRow = annotation.getSpecificDataMaterial(0)
	# 	print "after: " + str(dmRow.getDataItemInRow("cmax").value)
	# else:
	# 	print None

	return annotation


# query material items for claim annotation
# return list of MaterialItems
def queryMpMaterial(conn, annotation, claimid):

	qry = """	
	select mann.type, mf.material_field_type, mf.value_as_string, mf.value_as_number, s.exact, s.prefix, s.suffix, mp_data_index
	from mp_material_annotation mann,oa_material_body mbody, material_field mf, oa_target t, oa_selector s
	where mann.mp_claim_id = %s
	and mann.has_body = mbody.id
	and mf.material_body_id = mbody.id
	and mann.has_target = t.id
	and t.has_selector = s.id
	""" % (claimid)

	results = []

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():

		mType = row[0]  # material type
		mfType = row[1] # material field 

		value = row[2] or row[3] # value as string or number
		index = row[7] # data & material index

		if annotation.getSpecificDataMaterial(index) == None:
			dmRow = DataMaterialRow() # create new row of data & material

			if mType in ["object_dose","subject_dose"]: # dose
				doseItem = MaterialDoseItem(mType)
				doseItem.setAttribute(mfType, value)
				dmRow.setMaterialDoseItem(doseItem)
				annotation.setSpecificDataMaterial(dmRow, index)

			elif mType == "participants":
				partItem = ParticipantsItem()

		else: # current row of material & material exists 
			dmRow = annotation.getSpecificDataMaterial(index)

			if dmRow.getMaterialDoseInRow(mType) != None: # current MaterialItem exists
				doseItem = dmRow.getMaterialDoseInRow(mType)
				doseItem.setAttribute(mfType, value)
			else: # current MaterialItem not exists
				doseItem = MaterialDoseItem(mType) 
				doseItem.setAttribute(mfType, value)
				dmRow.setMaterialDoseItem(doseItem)
	return annotation

# query all mp annotations
# return annotations with claim, data and material
def queryMpAnnotation(conn):
	mpAnnotations = []
	claimAnnos = queryMpClaim(conn)

	cnt = 0

	for claimId,claimAnn in claimAnnos.items():
		if cnt > 6:
			break
		cnt += 1

		claimDataAnno = queryMpData(conn, claimAnn, claimId)
		claimDataMatAnno = queryMpData(conn, claimDataAnno, claimId)

		mpAnnotations.append(claimDataMatAnno)

	return mpAnnotations

######################### LOAD ##########################
def loadMpAnnotation(annotation):
	
	es = Elasticsearch(port=ES_PORT) # by default we connect to localhost:9200

	print "label(%s), subject(%s), predicate(%s), object(%s)" % (annotation.label, annotation.csubject, annotation.cpredicate, annotation.cobject)

	dmRows = annotation.getDataMaterials()
	
	if dmRows:
		firstRow = dmRows[1]
		for df in mpDataL:
			if firstRow.getDataItemInRow(df):
				print "%s: %s" % (df, str(firstRow.getDataItemInRow(df).value))
			else:
				print "%s: %s" % (df, None)

	mpAnn = loadTemplateInJson(MP_ANN_TEMPLATE)
	#print mpAnn["argues"]["hasTarget"]["hasSelector"]["@type"]

	#jsonbody = mpAnn
	#es.index(index="annotator", doc_type="annotation", id=uuid.uuid4(), body=jsonbody)

######################### CONFIG ##########################
# load json template
def loadTemplateInJson(path):
	json_data=open(path)
	data = json.load(json_data)
	json_data.close()
	return data

# postgres connection
def connectPostgres():

	dbconfig = file = open(DB_CONFIG)
	if dbconfig:
		for line in dbconfig:
			if "USERNAME" in line:
				DB_USER = line[(line.find("USERNAME=")+len("USERNAME=")):line.find(";")]
			elif "PASSWORD" in line:
				DB_PWD = line[(line.find("PASSWORD=")+len("PASSWORD=")):line.find(";")]
		conn = psycopg2.connect(host=HOSTNAME, user=DB_USER, password=DB_PWD, dbname=DB_SCHEMA)
		print("Postgres connection created")
	else:
		print "Postgres configuration file is not found: " + dbconfig

	return conn

######################### MAIN ##########################

def main():

	conn = connectPostgres()
	mpAnnotations = queryMpAnnotation(conn)	
	
	for mpAnn in mpAnnotations:
		loadMpAnnotation(mpAnn)		

	#printSample(mpAnnotations, 6)

	conn.close()


if __name__ == '__main__':
	main()

######################### TESTING ##########################
# print out sample annotation for validation
def printSample(mpannotations, idx):
	mpAnnotation = mpannotations[idx]
	dmRows = mpAnnotation.getDataMaterials()

	print "label(%s), subject(%s), predicate(%s), object(%s) " % (mpAnnotation.label, mpAnnotation.csubject, mpAnnotation.cpredicate, mpAnnotation.cobject)
	print "source: " + mpAnnotation.source
	#print "exact: " + mpAnnotation.exact	

	for index,dm in dmRows.items():	

		for df in mpDataL:
			if dm.getDataItemInRow(df):
				print "%s: %s" % (df, dm.getDataItemInRow(df).value)
		if dm.getMaterialDoseInRow("subject_dose"):
			print "subject_dose: %s" % (dm.getMaterialDoseInRow("subject_dose").value) 
		if dm.getMaterialDoseInRow("object_dose"):
			print "object_dose: %s" % (dm.getMaterialDoseInRow("object_dose").value)
		
