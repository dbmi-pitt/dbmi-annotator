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
from elastic import queryMPAnnotation as es
from model.Micropublication import *

HOME = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, HOME + '/model')

reload(sys)  
sys.setdefaultencoding('utf8')

######################### GLOBAL VARIABLES ##########################################
ES_PORT = 9200
PG_DATABASE = 'mpevidence'
MP_ANN_TEMPLATE = HOME + "/template/mp-annotation-template.json"
MP_DATA_TEMPLATE = HOME + "/template/mp-data-template.json"
HIGHLIGHT_TEMPLATE = HOME + "/template/highlight-annotation-template.json"

# dict for method name translate
methodL = ["DDI clinical trial", "Case Report", "Phenotype clinical study", "Statement"]

if len(sys.argv) > 5:
	PG_HOST = str(sys.argv[1])
	PG_USER = str(sys.argv[2])
	PG_PASSWORD = str(sys.argv[3])
	ES_HOSTNAME = str(sys.argv[4])
	AUTHOR = str(sys.argv[5])
else:
	print "Usage: load-rdb-annotations.py <pg hostname> <pg username> <pg password> <es hostname> <annotation author>"
	sys.exit(1)


def loadMpAnnotations(annotations, email):
	for ann in annotations:
		loadMpAnnotation(ann, email)	


def loadMpAnnotation(annotation, email):
	if isinstance(annotation, ClinicalTrial):
		mpAnn = createDDIClinicalTrialAnn(annotation, email)
		es = Elasticsearch([{'host': ES_HOSTNAME, 'port': ES_PORT}]) # by default we connect to localhost:9200  
		es.index(index="annotator", doc_type="annotation", id=annotation.urn, body=json.dumps(mpAnn))

######################### LOAD Annotations by method ################################
def createDDIClinicalTrialAnn(ann, email):

	mpAnn = loadTemplateInJson(MP_ANN_TEMPLATE) # load Annotation template
	addAnnotationMetaData(ann, mpAnn, email) # add annotation metadata

	## Claim
	csubject = ann.csubject; cpredicate = ann.cpredicate; cobject = ann.cobject; cqualifier = ann.cqualifier
	mpAnn["argues"]["hasTarget"] = generateOASelector(ann.prefix, ann.exact, ann.suffix)
	mpAnn["argues"]["label"] = ann.label
	mpAnn["argues"]["method"] =  ann.method # add method
	mpAnn["argues"]["negation"] = parseNegation(ann.negation) # add negation 
	mpAnn["argues"]["rejected"]["reason"] = parseEVRejected(ann) # EV rejected

	relationship = ann.cpredicate.qvalue # claim predicate
	mpAnn["argues"]["qualifiedBy"]["relationship"] = relationship

	## Qualifiers
	d1Qualifier = ann.getPrecipitantQualifier()
	d2Qualifier = ann.getObjectQualifier()
	mpAnn["argues"]["qualifiedBy"]["drug1"] = d1Qualifier.qvalue
	mpAnn["argues"]["qualifiedBy"]["drug1ID"] = d1Qualifier.qvalue + "_0"
	mpAnn["argues"]["qualifiedBy"]["drug2"] = d2Qualifier.qvalue
	mpAnn["argues"]["qualifiedBy"]["drug2ID"] = d2Qualifier.qvalue + "_0"
	mpAnn["argues"]["qualifiedBy"]["precipitant"] = "drug1"

	if relationship in ["inhibits", "substrate of"]:
		eQualifier = ann.getEnzyme()
		mpAnn["argues"]["qualifiedBy"]["enzyme"] = eQualifier.qvalue

	# MP Data & Material
	dmRows = ann.getDataMaterials()	
	for dmIdx,dmRow in dmRows.items(): # walk though all data items for claim
		mpData = loadTemplateInJson(MP_DATA_TEMPLATE) # load data & material template
		mpData["evRelationship"] = parseEvSupports(dmRow.ev_supports) # ev relation
		addAllDataRatios(dmRow, mpData) # add data ratio
		addEvQuestions(dmRow, mpData) # add evidence type questions

		if dmRow.participants: # add participants
			addParticipants(dmRow.participants, mpData)			
		if dmRow.precipitant_dose: # add drug1dose
			if dmRow.precipitant_dose.drugname == d1Qualifier.qvalue:
				addMaterialDose(dmRow.precipitant_dose, 1, mpData)
		if dmRow.object_dose: # add drug2dose
			if dmRow.object_dose.drugname == d2Qualifier.qvalue:
				addMaterialDose(dmRow.object_dose, 2, mpData)
		mpAnn["argues"]["supportsBy"].append(mpData)  # append data to annotation
	return mpAnn
		
## Translate and add MP Data or Material Item to JSON template ######################
def addAnnotationMetaData(ann, mpAnn, email):
	rawurl = ann.source; uri = re.sub(r"[\/\\\-\:\.]", "", rawurl)	
	mpAnn["created"] = "2017-01-12T18:33:51.179625+00:00" # Metadata
	mpAnn["updated"] = "2017-01-12T18:33:51.179625+00:00"
	if email:	
		mpAnn["email"] = email
	else:
		mpAnn["email"] = ann.creator
	mpAnn["rawurl"] = rawurl; mpAnn["uri"] = uri


def addAllDataRatios(dmRow, mpData):
	if dmRow.auc:
		addDataRatio(dmRow.auc, mpData)
	if dmRow.cmax:
		addDataRatio(dmRow.cmax, mpData)
	if dmRow.clearance:
		addDataRatio(dmRow.clearance, mpData)
	if dmRow.halflife:
		addDataRatio(dmRow.halflife, mpData)


def addDataRatio(drItem, mpData):
	dataType = drItem.field
	mpData[dataType]["hasTarget"] = generateOASelector(drItem.prefix, drItem.exact, drItem.suffix)
	mpData[dataType]["value"] = getattr(drItem, "value")
	mpData[dataType]["type"] = getattr(drItem, "type")
	mpData[dataType]["direction"] = getattr(drItem, "direction")


def addEvQuestions(dmRow, mpData):
	if dmRow.grouprandom:
		mpData["grouprandom"] = dmRow.grouprandom
	if dmRow.parallelgroup:
		mpData["parallelgroup"] = dmRow.parallelgroup


def addParticipants(pItem, mpData): 
	mpData["supportsBy"]["supportsBy"]["participants"]["hasTarget"] = generateOASelector(pItem.prefix, pItem.exact, pItem.suffix)
	mpData["supportsBy"]["supportsBy"]["participants"]["ranges"] = []
	mpData["supportsBy"]["supportsBy"]["participants"]["value"] = pItem.value
	

## add specific material dose to data JSON template
# param1: MaterialDoseItem
# param2: drug index (1 or 2)
# param3: data JSON template
def addMaterialDose(dsItem, drugIdx, mpData):
	if drugIdx in [1,2] and dsItem and mpData:
		mpData["supportsBy"]["supportsBy"]["drug"+str(drugIdx)+"Dose"]["hasTarget"] = generateOASelector(dsItem.prefix, dsItem.exact, dsItem.suffix)
		mpData["supportsBy"]["supportsBy"]["drug"+str(drugIdx)+"Dose"]["ranges"] = []
		mpData["supportsBy"]["supportsBy"]["drug"+str(drugIdx)+"Dose"]["value"] = dsItem.value
		mpData["supportsBy"]["supportsBy"]["drug"+str(drugIdx)+"Dose"]["duration"] = dsItem.duration
		mpData["supportsBy"]["supportsBy"]["drug"+str(drugIdx)+"Dose"]["formulation"] = dsItem.formulation
		mpData["supportsBy"]["supportsBy"]["drug"+str(drugIdx)+"Dose"]["regimens"] = dsItem.regimens
	else:
		print "[ERROR] translateRDB2Elastic: addMaterialDose exception!"

	
## Parse MP Model to JSON attributes for annotation in Elasticsearch ############### 
def parseNegation(negation):
	if negation == True:
		return "Yes"
	elif negation == False:
		return "No"
	else:
		return None


def parseEVRejected(ann):
	if ann.rejected_statement and ann.rejected_statement_reason or ann.rejected_statement_comment:
		return ann.rejected_statement_reason + "|" + ann.rejected_statement_comment
	else:
		return None


def parseEvSupports(ev_supports):
	if ev_supports == True:
		return "supports"
	elif ev_supports == False:
		return "refutes"


# load mp annotation to specific account by email
#def loadMpAnnotation(annotation, email):			
	# # MP Data & Material
	# dmRows = annotation.getDataMaterials()	
	# for index,dmRow in dmRows.items(): # walk though all data items for claim
		
	# 	mpData = loadTemplateInJson(MP_DATA_TEMPLATE) # data template
		
	# 	# MP Data - dips questions
	# 	dataDips = dmRow.getDataDips()
	# 	if dataDips:
	# 		dipsQsD = dataDips.getDipsDict()
	# 		if dipsQsD and isinstance(dipsQsD, dict):
	# 			for qs in dipsQsD:
	# 				mpData["dips"][qs] = dipsQsD[qs]
	# 	print mpData["dips"]

	# 	# MP Data - reviewer		
	# 	reviewer = dmRow.getDataReviewer()
	# 	if reviewer:
	# 		mpData["reviewer"]["reviewer"] = reviewer.reviewer
	# 		mpData["reviewer"]["date"] = reviewer.date
	# 		mpData["reviewer"]["total"] = reviewer.total
	# 		mpData["reviewer"]["lackInfo"] = reviewer.lackinfo

	# 	# MP Material
	# 	if dmRow.getPhenotype():		
	# 		mpData["supportsBy"]["supportsBy"]["phenotype"]["type"] = dmRow.getPhenotype().ptype
	# 		mpData["supportsBy"]["supportsBy"]["phenotype"]["value"] = dmRow.getPhenotype().value
	# 		mpData["supportsBy"]["supportsBy"]["phenotype"]["metabolizer"] = dmRow.getPhenotype().metabolizer
	# 		mpData["supportsBy"]["supportsBy"]["phenotype"]["population"] = dmRow.getPhenotype().population		


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


# load json template from file
def loadTemplateInJson(path):
	json_data=open(path)
	data = json.load(json_data)
	json_data.close()
	return data


######################### MAIN ######################################################
def main():

	conn = pgconn.connect_postgres(PG_HOST, PG_USER, PG_PASSWORD, PG_DATABASE)
	pgconn.setDbSchema(conn, "ohdsi")

	annotations = pgqry.getMpAnnotations(conn)	
	loadMpAnnotations(annotations, AUTHOR)

	#highlightD = pgqry.queryHighlightAnns(conn)
	#print highlightD
	#loadHighlightAnnotations(highlightD, AUTHOR)

	conn.close()
	print "[INFO] elasticsearch load completed"

if __name__ == '__main__':
	main()

		
