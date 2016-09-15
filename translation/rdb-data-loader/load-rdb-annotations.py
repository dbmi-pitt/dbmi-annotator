import csv
import psycopg2
import uuid
import datetime

# DB connection config
hostname = 'localhost'
username = 'postgres'
password = 'ning1fan'
database = 'mpevidence'


# Parent class of data or material item
class dmItem:
	prefix = ""
	exact = ""
	suffix = ""
	dmIdx = 0

	def setDmItem(self, prefix, exact, suffix):
		dmItem.prefix = prefix
		dmItem.exact = exact
		dmItem.suffix = suffix
		
	def getDmIdx():
		return dmItem.dmIdx

	def setDmIdx(idx):
		dmItem.dmIdx = idx

# Data item in row of data 
class DataItem(dmItem):
	def __init__(self, field, value, type, direction):
		self.field = field # options: auc, cmax, clearance, halflife
		self.value = value 
		self.type = type
		self.direction = direction

# Material dose item
class MaterialDoseItem(dmItem):
	def __init__(self, field, value, duration, formulation, regimens):
		self.field = field # options: objectdose or subjectdose
		self.value = value 
		self.duration = duration
		self.formulation = formulation
		self.regimens = regimens

# Material participant item
class MatarialParticipants(dmItem):
	def __init__(self, value):
		self.value = value


# represents single row of data & material in annotation table
class DataMaterialRow(object):

	index = 0 # mp data index for claim, default 0 
	dataMaterialRowD = {"auc": None, "cmax": None, "clearance": None, "halflife": None, "participants": None, "objectdose": None, "subjectdose": None}

	def addDataItem(obj):
		if dataMartialRowD[obj.field] != None:
			print "[Warning] Data item already has the field: " + obj.field
		elif obj.field in ["auc", "cmax", "clearance", "halflife"]:
			dataMartialRowD[obj.field] = obj
		else:
			print "[Error] data item undefined: " + obj.field

	def addMaterialItem(obj):
		if dataMartialRowD[obj.field] != None:
			print "[Warning] Data item already has the field: " + obj.field
		elif obj.field in ["subjectdose", "objectdose"]:
			dataMartialRowD[obj.field] = obj			
		else:
			print "[Error] material item undefined: " + obj.field

	def addParticipants(obj):
		if dataMartialRowD["participants"] != None:
			print "[Warning] Data item already has the field: participants"
		else:
			dataMartialRowD["participants"] = obj
	# get one row of data & material items		
	def getDataMaterialRow():
		return self.dataMaterialRowD


# Define data structure for mp annotation
class Annotation(object):
	csubject = ""
	cpredicate = ""
	cobject = ""
	label = ""

	mpDataMaterialD = {}

	def addDataMaterialRow(dmRow):
		if mpDataMaterialD[dmRow.getDmIdx()] == None:
			mpDataMaterialD[dmRow.getDmIdx()] = dmRow.getDataMaterialRow()
		else:
			print "[Warning] Data row already been filled - index: " + dmRow.getDmIdx()

	def getDataMaterial():
		return self.mpDataMaterialD


# query mp claim annotation by author name
# return claim s, p, o and oa selector
def queryMpClaim(conn):
	qry = """select cann.id, t.has_source, cann.creator, cann.date_created, s.exact, cbody.label, qvalue, q.subject, q.predicate, q.object 
	from mp_claim_annotation cann, oa_claim_body cbody, oa_target t, oa_selector s, qualifier q
	where cann.has_body = cbody.id
	and cann.has_target = t.id
	and t.has_selector = s.id
	and cbody.id = q.claim_body_id"""

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():
		#print(row[1])
		annotation = Annotation()
		annotation.csubject = row[7]
		annotation.cpredicate = row[8]
		annotation.cobject = row[9]

		#print annotation


######################### MAIN ##########################

def main():

    print("postgres connection ...")
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    #delete all data in table
    #clearall(myConnection)
    #myConnection.commit()

    queryMpClaim(conn)
    conn.close()


if __name__ == '__main__':
    main()


'''
-- validate context 
select cann.id, cann.has_target, dann.has_target, mann.has_target
from mp_claim_annotation cann, mp_data_annotation dann, mp_material_annotation mann
where cann.id = dann.mp_claim_id and cann.id = mann.mp_claim_id;

-- validate claim
select cann.id, t.has_source, cann.creator, cann.date_created, cann.has_target, s.exact
from mp_claim_annotation cann, mp_data_annotation dann, mp_material_annotation mann, 
oa_target t, oa_selector s
where cann.id = dann.mp_claim_id 
and cann.id = mann.mp_claim_id
and cann.has_target = t.id
and t.has_selector = s.id;

-- query mp claim

'''
