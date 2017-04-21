import sys, csv, json, re, os
import uuid
import datetime, copy
from elasticsearch import Elasticsearch
from sets import Set
#from model.micropublication import Annotation, DataMaterialRow, DMItem, DataRatioItem, MaterialDoseItem, MaterialParticipants, MaterialPhenotypeItem, DataReviewer, DataDips
sys.path.append("../")
from model.Micropublication import *

## create customized document based on template
## rtype null
def createMpAnnotation(host, port, annotation, annotationId):
	es = Elasticsearch([{'host': host, 'port': port}]) 
	es.index(index="annotator", doc_type="annotation", id=annotationId, body=json.dumps(annotation))

## query documents by json format query condition
## rtype json documents
def queryByBody(host, port, doc):
	es = Elasticsearch([{'host': host, 'port': port}])
	res = es.search(index="annotator", size="5000", body=doc)	
	# print("Got %d Hits:" % res['hits']['total'])
	return res

def queryById(host, port, annotationId):
	es = Elasticsearch([{'host': host, 'port': port}])
	res = es.get(index="annotator", id = annotationId)	
	return res

## delete document by id
## rtype null
def deleteById(host, port, annotationId):
	es = Elasticsearch([{'host': host, 'port': port}])
	es.delete(index="annotator", doc_type="annotation", id=annotationId)


def getMPAnnsByBody(es_host, es_port, query_condit):
	## query condition (refers to elasticsearch REST API)
	body = {'query': { 'term': {'annotationType': 'MP'}}}
	if query_condit:
		body = query_condit

	res = queryByBody(es_host, es_port, body)	
	docs = res['hits']['hits']
	annsL = parseToMPAnns(docs)

	return annsL

def parseToMPAnns(documents):
	anns = []
	for doc in documents:
		ann = parseToMPAnn(doc)
		if ann:
			anns.append(ann)
	return anns

def parseToMPAnn(document):
	doc = document["_source"]; doc_urn = document["_id"]
	method = doc["argues"]["method"];
	annotation = None

	if method == "DDI clinical trial":
		annotation = createClinicalTrial(doc, doc_urn)

	return annotation

def parseEvSupports(evRelationship):
	if evRelationship == "supports":
		return True
	elif evRelationship in ["refutes", "challenges"]:
		return False
	return True

def addAnnotationMetadata(annotation, urn, source, email, date_created, label):
	if not urn or not source or not email:
		print "[ERROR] Json annotation error, skip source (%s), claim (%s)" % (source, label)
	annotation.urn = urn
	annotation.source = source
	annotation.creator = email
	annotation.label = label
	annotation.date_created = date_created
	

## DDI CLINICAL TRIAL ##############################################################
## initial clinical trial annotation
# param1: annotation in Json from elasticsearch
# param2: annotation Id
# return: Clinical trial annotation
def createClinicalTrial(doc, doc_urn):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	label = claim["label"]
	exact = getSelectorTxt(claim, "exact"); prefix = getSelectorTxt(claim, "prefix"); suffix = getSelectorTxt(claim, "suffix")

	qualifier = claim["qualifiedBy"]; 

	if "precipitant" not in qualifier:
		print "[ERROR] createClinicalTrial: percipitant undefined, skip source (%s), claim (%s)" % (source, label)
		return None

	drugname1 = qualifier["drug1"]; drugname2 = qualifier["drug2"]; enzyme = qualifier["enzyme"]; predicate = qualifier["relationship"]; precipitant = qualifier["precipitant"]

	if "drug1PC" in qualifier:		
		drug1PC = qualifier["drug1PC"]
	else:
		drug1PC = None
	
	if "drug2PC" in qualifier:
		drug2PC = qualifier["drug2PC"]
	else:
		drug2PC = None

	## data validation
	if precipitant not in ["drug1","drug2"] or ((predicate == "interact with" and (not drugname1 or not drugname2 or enzyme)) or (predicate in ["inhibits", "substrate of"] and (not drugname1 or not drugname2 or not enzyme))): 
		print "[WARN] DDI clinical trial: qualifier error, skip (%s) - (%s)" % (source, label)
		return None
	
	## MP Claim
	annotation = ClinicalTrial()
	addAnnotationMetadata(annotation, doc_urn, source, email, doc["created"], label)
	addQualifiersForCT(annotation, drugname1, drugname2, predicate, enzyme, precipitant, drug1PC, drug2PC)
	annotation.setOaSelector(prefix, exact, suffix)

	## MP Data
	dataL = claim["supportsBy"]
	if dataL and len(dataL) > 0:
		for i in xrange(0, len(dataL)):
			data = dataL[i]
			dmRow = ClinicalTrialDMRow(i)
			dmRow.ev_supports = parseEvSupports(data["evRelationship"]) 

			for ratioType in ["auc", "cmax", "clearance", "halflife"]:
				if data[ratioType]:
					ratioItem = createDataRatioItem(data[ratioType], ratioType)	
					setattr(dmRow, ratioType, ratioItem)
 
			material = data["supportsBy"]["supportsBy"]
			if material:
				if material["participants"]:
					participants = createParticipantsItem(material["participants"])
					dmRow.participants = participants

				cprecipitant = annotation.getPrecipitantQualifier()
				cobject = annotation.getObjectQualifier()
				preciptDose = None; objectDose = None
				if material["drug1Dose"]:
					if drugname1 == cprecipitant.qvalue: ## drug1 is precipitant
						preciptDose = createDoseItem(material["drug1Dose"], "precipitant", drugname1)				
					elif drugname1 == cobject.qvalue: ## drug1 is object
						objectDose = createDoseItem(material["drug1Dose"], "object", drugname1)
				if material["drug2Dose"]:
					if drugname2 == cprecipitant.qvalue: ## drug2 is precipitant
						preciptDose = createDoseItem(material["drug2Dose"], "precipitant", drugname2)
						dmRow.precipitant_dose = preciptDose					
					elif drugname2 == cobject.qvalue: ## drug2 is object
						objectDose = createDoseItem(material["drug2Dose"], "object", drugname2)

				if preciptDose:
					dmRow.precipitant_dose = preciptDose	
				if objectDose:
					dmRow.object_dose = objectDose

			annotation.setSpecificDataMaterial(dmRow, i) # add new row of data and material			
	return annotation

def createDoseItem(item, doseType, drugname):

	if doseType in ["precipitant", "object", "probesubstrate"] or not drugname:
		dose = MaterialDoseItem(doseType)
		value = item["value"]
		formulation = item["formulation"]
		duration = item["duration"]
		regimens = item["regimens"]
		exact = getSelectorTxt(item, "exact"); prefix = getSelectorTxt(item, "prefix"); suffix = getSelectorTxt(item, "suffix")
		dose.setAttributes(drugname, value, formulation, duration, regimens)
		dose.setSelector(prefix, exact, suffix)
		return dose
	else:
		print "[ERROR] createDoseItem: (%s) doseType undefined %s" % (drugname, doseType)
	return None

def createParticipantsItem(item):
	part = MaterialParticipants(item["value"])
	exact = getSelectorTxt(item, "exact"); prefix = getSelectorTxt(item, "prefix"); suffix = getSelectorTxt(item, "suffix")
	part.setSelector(prefix, exact, suffix)
	return part

def createDataRatioItem(item, ratioType):	

	if ratioType in ["auc","cmax","clearance","halflife"]:
		dataRatio = DataRatioItem(ratioType)
		rVal = item["value"]
		rType= item["type"]
		rDirection = item["direction"]
		exact = getSelectorTxt(item, "exact"); prefix = getSelectorTxt(item, "prefix"); suffix = getSelectorTxt(item, "suffix")
		dataRatio.setAttributes(rVal, rType, rDirection)
		dataRatio.setSelector(prefix, exact, suffix)
		return dataRatio
	else:
		print "[ERROR] createDataRatioItem: ratioType undefined %s" % ratioType
	return None
	
## add qualifiers to Clinical trial annotation
# parma1: annotation obj
# param2: drug1 name
# param3: drug2 name
# param4: DDI relationship
# param5: enzyme
# param6: precipitant in DDI
# param7: drug1 parent compound
# param8: drug2 parent compound
def addQualifiersForCT(annotation, drugname1, drugname2, predicate, enzyme, precipitant, drug1PC, drug2PC):
	csubject = None; cobject = None; cqualifier = None

	if predicate == "interact with":
		if precipitant == "drug1":
			csubject = Qualifier(drugname1, True, False, False) # drug1 as mpsubject/precipitant
			csubject.setRolePrecipitant()
			csubject.setTypeDrugProduct()
			addParentCompound(csubject, drug1PC)
			
			cobject = Qualifier(drugname2, False, False, True) # drug2 as mpobject/ddiobject
			cobject.setRoleObject()
			cobject.setTypeDrugProduct()
			addParentCompound(cobject, drug2PC)
		else:
			csubject = Qualifier(drugname2, True, False, False) # drug2 as mpsubject/precipitant
			csubject.setRolePrecipitant()
			csubject.setTypeDrugProduct()
			addParentCompound(csubject, drug2PC)			
			
			cobject = Qualifier(drugname1, False, False, True) # drug1 as mpobject/ddiobject
			cobject.setRoleObject()
			cobject.setTypeDrugProduct()
			addParentCompound(cobject, drug1PC)							

	elif predicate == "inhibits":
		if precipitant == "drug1":
			csubject = Qualifier(drugname1, True, False, False) # drug1 as mpsubject/precipitant
			csubject.setRolePrecipitant()
			csubject.setTypeDrugProduct()
			addParentCompound(csubject, drug1PC)				

			cobject = Qualifier(enzyme, False, False, True) # enzyme as mpobject
			cobject.setTypeEnzyme()
			
			cqualifier = Qualifier(drugname2, False, False, False) # drug2 as ddiobject
			cqualifier.setRoleObject()
			cqualifier.setTypeDrugProduct()
			addParentCompound(cqualifier, drug2PC)				
		else:
			csubject = Qualifier(drugname2, True, False, False) # drug2 as mpsubject/precipitant
			csubject.setRolePrecipitant()
			csubject.setTypeDrugProduct()
			addParentCompound(csubject, drug2PC)				

			cobject = Qualifier(enzyme, False, False, True) # enzyme as mpobject
			cobject.setTypeEnzyme()

			cqualifier = Qualifier(drugname1, False, False, False) # drug1 as ddiobject
			cqualifier.setRoleObject()
			cqualifier.setTypeDrugProduct()
			addParentCompound(cqualifier, drug1PC)	

	else: # predicate is "substrate of"
		if precipitant == "drug1":
			csubject = Qualifier(drugname2, True, False, False) # drug2 as mpsubject/ddiobject
			csubject.setRoleObject()
			csubject.setTypeDrugProduct()
			addParentCompound(csubject, drug2PC)				

			cobject = Qualifier(enzyme, False, False, True) # enzyme as mpobject
			cobject.setTypeEnzyme()

			cqualifier = Qualifier(drugname1, False, False, False) # drug1 as precipitant
			cqualifier.setRolePrecipitant()
			cqualifier.setTypeDrugProduct()
			addParentCompound(cqualifier, drug1PC)				
		else:
			csubject = Qualifier(drugname1, True, False, False) # drug1 as mpsubject/ddiobject
			csubject.setRoleObject()
			csubject.setTypeDrugProduct()
			addParentCompound(csubject, drug1PC)				
			
			cobject = Qualifier(enzyme, False, False, True) # enzyme as mpobject
			cobject.setTypeEnzyme()
				
			cqualifier = Qualifier(drugname2, False, False, False) # drug2 as precipitant
			cqualifier.setRolePrecipitant()
			cqualifier.setTypeDrugProduct()
			addParentCompound(cqualifier, drug2PC)	
		
	cpredicate = Qualifier(predicate, False, True, False)
	annotation.setQualifiers(csubject, cpredicate, cobject, cqualifier)


## add parent compound to qualifier		
# param1: Qualifier
# param2: drugPC string from AnnotationPress "enantiomer|metabolite"
def addParentCompound(qualifier, drugPC):
	if drugPC and "|" in drugPC:
		pcL = drugPC.split("|") 
		[enantiomer, metabolite] = [isPC(pcL[0]), isPC(pcL[1])]
		qualifier.enantiomer = enantiomer
		qualifier.metabolite = metabolite

## get text span based OA target, selector
# param1: object with attri hasTarget
# param2: oa selector span type: prefix, exact, suffix
# return: specific text in OA selector
def getSelectorTxt(field, spanType):
	if spanType not in ["prefix", "exact", "suffix"]:
		print "[ERROR] getSelectorTxt spanType undefined %s" % spanType
		return None

	if field["hasTarget"]:
		if field["hasTarget"]["hasSelector"]:
			if spanType == "prefix":
				return field["hasTarget"]["hasSelector"]["prefix"]
			elif spanType == "exact":
				return field["hasTarget"]["hasSelector"]["exact"]
			else:
				return field["hasTarget"]["hasSelector"]["suffix"]
	return None

## convert parent compound from string in AnnotationPress to boolean for Annotation
# param1: "enantiomer|metabolite"
# return: boolean for "enantiomer", "metabolite"
def isPC(pcStr):
	if pcStr in ["enantiomer", "metabolite"]:
		return True
	else:
		return False

def test():
	query_condit = {'query': { 'term': {'annotationType': 'MP'}}}
	anns = getMPAnnsByBody("localhost", "9200", query_condit)
	print anns

######################### MAIN ###################################################

def main():
	test()
	

if __name__ == '__main__':
	main()
