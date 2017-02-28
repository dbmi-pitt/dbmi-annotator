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

import sys, csv, json, re, os
import uuid
import datetime
from elasticsearch import Elasticsearch

from postgres import connection as pgconn
from postgres import mpEvidenceLoad as pgmp
from postgres import mpEvidenceQry as pgqry
from postgres import omopConceptQry as pgcp
from elastic import queryAnnsInElastico as es

from model.micropublication import Annotation, DataMaterialRow, DMItem, DataRatioItem, MaterialDoseItem, MaterialParticipants, MaterialPhenotypeItem, DataReviewer, DataDips

HOME = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, HOME + '/model')
#from micropublication import Annotation, DataMaterialRow, DMItem, DataItem, MaterialDoseItem, MaterialParticipants

reload(sys)  
sys.setdefaultencoding('utf8')

######################### VARIABLES ##########################
ES_PORT = 9200
PG_DATABASE = 'mpevidence'
MP_ANN_TEMPLATE = HOME + "/template/mp-annotation-template.json"
MP_DATA_TEMPLATE = HOME + "/template/mp-data-template.json"
HIGHLIGHT_TEMPLATE = HOME + "/template/highlight-annotation-template.json"

# list of data items
mpDataL = ["auc", "cmax", "clearance", "halflife"]

# dict for method name translate
methodM = {"clinical trial": "DDI clinical trial", "statement": "Statement", "Phenotype clinical study": "Phenotype clinical study", "Case Report": "Case Report"}

if len(sys.argv) > 5:
	PG_HOST = str(sys.argv[1])
	PG_USER = str(sys.argv[2])
	PG_PASSWORD = str(sys.argv[3])
	ES_HOSTNAME = str(sys.argv[4])
	AUTHOR = str(sys.argv[5])
else:
	print "Usage: load-rdb-annotations.py <pg hostname> <pg username> <pg password> <es hostname> <annotation author>"
	sys.exit(1)


######################### LOAD ##########################

# return oa selector in json
def generateOASelector(prefix, exact, suffix):

	oaSelector = "{\"hasSelector\": { \"@type\": \"TextQuoteSelector\", \"exact\": \""+unicode(exact or "", "utf-8")+"\", \"prefix\": \""+ unicode(prefix or "", "utf-8") + "\", \"suffix\": \"" + unicode(suffix or "", "utf-8") + "\"}}"

	return json.loads(oaSelector, strict=False)

# load highlight annotations to documents
def loadHighlightAnnotations(highlightD, email):

	for url in highlightD:
		if len(highlightD[url]) > 0:
			for name in highlightD[url]:
				loadHighlightAnnotation(url, name, email)


# load highlight annotation to specific account by email
def loadHighlightAnnotation(rawurl, content, email):

	#if "036db1f2-52b3-42a0-acf9-817b7ba8c724" not in rawurl:
	#	return

	annotation = loadTemplateInJson(HIGHLIGHT_TEMPLATE)

	oaSelector = generateOASelector("", content, "")
	annotation["argues"]["hasTarget"] = oaSelector

	uri = re.sub(r"[\/\\\-\:\.]", "", rawurl)
	annotation["rawurl"] = rawurl # Document source url
	annotation["uri"] = uri

	annotation["email"] = email # Metadata
	annotation["created"] = "2016-09-19T18:33:51.179625+00:00" 
	annotation["updated"] = "2016-09-19T18:33:51.179625+00:00"

	es = Elasticsearch(hosts = [{'host': ES_HOSTNAME, 'port': ES_PORT}]) # by default we connect to localhost:9200	
	es.index(index="annotator", doc_type="annotation", id=uuid.uuid4(), body=json.dumps(annotation))

# load mp annotation to specific account by email
def loadMpAnnotation(annotation, email):		

	subjectDrug = annotation.csubject; predicate = annotation.cpredicate; objectDrug = annotation.cobject
	prefix = annotation.prefix; exact = annotation.exact; suffix = annotation.suffix
	rawurl = annotation.source
	uri = re.sub(r"[\/\\\-\:\.]", "", rawurl)
	label = annotation.label.replace("interact_with","interact with")

	mpAnn = loadTemplateInJson(MP_ANN_TEMPLATE)
	claimSelector = generateOASelector(prefix, exact, suffix)

	print "[INFO] Load doc(%s), subject(%s), predicate(%s), object(%s) \n" % (rawurl, annotation.csubject, annotation.cpredicate, annotation.cobject)

	# MP Claim
	mpAnn["argues"]["method"] = methodM[annotation.method] # method name translate

	if annotation.negation == True:
		mpAnn["argues"]["negation"] = "Yes"
	elif annotation.negation == False:
		mpAnn["argues"]["negation"] = "No"

	mpAnn["argues"]["rejected"]["reason"] = annotation.rejected

	mpAnn["argues"]["qualifiedBy"]["drug1"] = subjectDrug
	mpAnn["argues"]["qualifiedBy"]["drug2"] = objectDrug
	mpAnn["argues"]["qualifiedBy"]["drug1ID"] = subjectDrug + "_1"
	mpAnn["argues"]["qualifiedBy"]["drug2ID"] = objectDrug + "_1"

	mpAnn["argues"]["qualifiedBy"]["relationship"] = predicate.replace("interact_with","interact with")
	mpAnn["argues"]["qualifiedBy"]["precipitant"] = "drug1" # for interact_with
	mpAnn["argues"]["hasTarget"] = claimSelector
	
	# MP Data & Material
	dmRows = annotation.getDataMaterials()	

	for index,dmRow in dmRows.items(): # walk though all data items for claim
		
		mpData = loadTemplateInJson(MP_DATA_TEMPLATE) # data template
		
		# MP Data - auc, cmax, clearance, halflife
		for df in mpDataL: 
		 	if dmRow.getDataRatioItemInRow(df):
				mpData[df]["value"] = str(dmRow.getDataRatioItemInRow(df).value)
				mpData[df]["type"] = str(dmRow.getDataRatioItemInRow(df).type)
				mpData[df]["direction"] = str(dmRow.getDataRatioItemInRow(df).direction)
				dataExact = dmRow.getDataRatioItemInRow(df).exact
				dataSelector = generateOASelector("", dataExact, "")
				mpData[df]["hasTarget"] = dataSelector
				mpData[df]["ranges"] = []

		mpData["grouprandom"] = dmRow.getGroupRandom()
		mpData["parallelgroup"] = dmRow.getParallelGroup()

		# MP Data - dips questions
		dipsQsL = dmRow.getDataDips()
		if dipsQsL and isinstance(dipsQsL, list):
			for i in xrange(0,len(dipsQsL)):
				mpData["dips"]["q" + str(i+1)] = dipsQsL[i]

		# MP Data - reviewer		
		reviewer = dmRow.getDataReviewer()
		if reviewer:
			mpData["reviewer"]["reviewer"] = reviewer.reviewer
			mpData["reviewer"]["date"] = reviewer.date
			mpData["reviewer"]["total"] = reviewer.total
			mpData["reviewer"]["lackinfo"] = reviewer.lackinfo

		# MP Material
		if dmRow.getParticipantsInRow():
			partExact = dmRow.getParticipantsInRow().exact
			partSelector = generateOASelector("", partExact, "")
			mpData["supportsBy"]["supportsBy"]["participants"]["value"] = dmRow.getParticipantsInRow().value
			mpData["supportsBy"]["supportsBy"]["participants"]["hasTarget"] = partSelector
			mpData["supportsBy"]["supportsBy"]["participants"]["ranges"] = []

		if dmRow.getMaterialDoseInRow("subject_dose"):
			subDoseExact = dmRow.getMaterialDoseInRow("subject_dose").exact
			subDoseSelector = generateOASelector("", subDoseExact, "")
			mpData["supportsBy"]["supportsBy"]["drug1Dose"]["value"] = dmRow.getMaterialDoseInRow("subject_dose").value
			mpData["supportsBy"]["supportsBy"]["drug1Dose"]["duration"] = dmRow.getMaterialDoseInRow("subject_dose").duration
			mpData["supportsBy"]["supportsBy"]["drug1Dose"]["formulation"] = dmRow.getMaterialDoseInRow("subject_dose").formulation
			mpData["supportsBy"]["supportsBy"]["drug1Dose"]["regimens"] = dmRow.getMaterialDoseInRow("subject_dose").regimens
			mpData["supportsBy"]["supportsBy"]["drug1Dose"]["hasTarget"] = subDoseSelector
			mpData["supportsBy"]["supportsBy"]["drug1Dose"]["ranges"] = []

		if dmRow.getMaterialDoseInRow("object_dose"):
			objDoseExact = dmRow.getMaterialDoseInRow("object_dose").exact
			objDoseSelector = generateOASelector("", objDoseExact, "")
			mpData["supportsBy"]["supportsBy"]["drug2Dose"]["value"] = dmRow.getMaterialDoseInRow("object_dose").value
			mpData["supportsBy"]["supportsBy"]["drug2Dose"]["duration"] = dmRow.getMaterialDoseInRow("object_dose").duration
			mpData["supportsBy"]["supportsBy"]["drug2Dose"]["formulation"] = dmRow.getMaterialDoseInRow("object_dose").formulation
			mpData["supportsBy"]["supportsBy"]["drug2Dose"]["regimens"] = dmRow.getMaterialDoseInRow("object_dose").regimens
			mpData["supportsBy"]["supportsBy"]["drug2Dose"]["hasTarget"] = objDoseSelector
			mpData["supportsBy"]["supportsBy"]["drug2Dose"]["ranges"] = []

		if dmRow.getPhenotype():		
			mpData["supportsBy"]["supportsBy"]["phenotype"]["type"] = dmRow.getPhenotype().ptype
			mpData["supportsBy"]["supportsBy"]["phenovalue"]["value"] = dmRow.getPhenovalue().value
			mpData["supportsBy"]["supportsBy"]["phenometabolizer"]["metabolizer"] = dmRow.getPhenometabolizer().metabolizer
			mpData["supportsBy"]["supportsBy"]["phenotype"]["population"] = dmRow.getPhenotype().population
			

		mpData["evRelationship"] = dmRow.getEvRelationship()
		mpAnn["argues"]["supportsBy"].append(mpData)  # append mp data to claim

	mpAnn["created"] = "2016-09-19T18:33:51.179625+00:00" # Metadata
	mpAnn["updated"] = "2016-09-19T18:33:51.179625+00:00"
	mpAnn["email"] = email

	mpAnn["argues"]["label"] = label
	mpAnn["rawurl"] = rawurl # Document source url
	mpAnn["uri"] = uri

	es = Elasticsearch([{'host': ES_HOSTNAME, 'port': ES_PORT}]) # by default we connect to localhost:9200  
	es.index(index="annotator", doc_type="annotation", id=uuid.uuid4(), body=json.dumps(mpAnn))

######################### CONFIG ##########################
# load json template
def loadTemplateInJson(path):

	json_data=open(path)
	data = json.load(json_data)
	json_data.close()
	return data

######################### TESTING ##########################
# print out sample annotation for validation
def printSample(mpannotations, idx):
	mpAnnotation = mpannotations[idx]
	dmRows = mpAnnotation.getDataMaterials()

	print "label(%s), subject(%s), predicate(%s), object(%s) " % (mpAnnotation.label, mpAnnotation.csubject, mpAnnotation.cpredicate, mpAnnotation.cobject)

	for index,dm in dmRows.items():	

		for df in mpDataL:
			if dm.getDataItemInRow(df):
				print "%s: %s" % (df, dm.getDataItemInRow(df).value)
		if dm.getMaterialDoseInRow("subject_dose"):
			print "subject_dose: %s" % (dm.getMaterialDoseInRow("subject_dose").value) 
		if dm.getMaterialDoseInRow("object_dose"):
			print "object_dose: %s" % (dm.getMaterialDoseInRow("object_dose").value)



######################### MAIN ##########################

def main():

	conn = pgconn.connect_postgres(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	mpAnnotations = pgqry.queryAllMpAnnotation(conn)	
	
	for mpAnn in mpAnnotations:
		#if mpAnn.source in ["http://localhost/DDI-labels/829a4f51-c882-4b64-81f3-abfb03a52ebe.html"] :
		loadMpAnnotation(mpAnn, AUTHOR)		

	highlightD = pgqry.queryHighlightAnns(conn)

	#print highlightD
	loadHighlightAnnotations(highlightD, AUTHOR)

	conn.close()
	print "[INFO] elasticsearch load completed"

if __name__ == '__main__':
	main()

		
