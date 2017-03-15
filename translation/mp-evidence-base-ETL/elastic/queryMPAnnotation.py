import sys, csv, json, re, os
import uuid
import datetime, copy
from elasticsearch import Elasticsearch
from sets import Set
sys.path.append("../")
from elastic import operations as esop
from model.Micropublication import *

def getMPAnnsByBody(es_host, es_port, query_condit):
	## query condition (refers to elasticsearch REST API)
	body = {'query': { 'term': {'annotationType': 'MP'}}}
	if query_condit:
		body = query_condit

	res = esop.queryByBody(es_host, es_port, body)	
	docs = res['hits']['hits']
	annsL = parseToMPAnns(docs)

	return annsL

def getMPAnnById(es_host, es_port, annId):
	res = esop.queryById(es_host, es_port, annId)	
	ann = parseToMPAnn(res)
	return ann

def parseToMPAnns(documents):
	anns = []
	for doc in documents:
		ann = parseToMPAnn(doc)
		if ann:
			anns.append(ann)
	return anns
	

## DDI CLINICAL TRIAL ##############################################################
## initial clinical trial annotation
# param1: annotation in Json from elasticsearch
# param2: annotation Id
# return: Clinical trial annotation
def createClinicalTrial(doc, doc_urn):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	label = claim["label"]; method = doc["argues"]["method"]; date = doc["created"]
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
	annotation = createSubAnnotation(doc_urn, source, label, method, email, date)
	addQualifiersForCT(annotation, drugname1, drugname2, predicate, enzyme, precipitant, drug1PC, drug2PC)
	annotation.setOaSelector(prefix, exact, suffix)
	addRejected(annotation, claim)
	annotation.method = method ## MP Method

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


## add parent compound to qualifier		
# param1: Qualifier
# param2: drugPC string from AnnotationPress "enantiomer|metabolite"
def addParentCompound(qualifier, drugPC):
	if drugPC and "|" in drugPC:
		pcL = drugPC.split("|") 
		[enantiomer, metabolite] = [isPC(pcL[0]), isPC(pcL[1])]
		qualifier.enantiomer = enantiomer
		qualifier.metabolite = metabolite


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

	
def addRejected(annotation, claim):
	# ## statement rejection 
	rej_statement = False; rej_reason = None; rej_comment = None
	if claim["rejected"]["reason"]:
		rej_statement = True
		if '|' in claim["rejected"]["reason"]:
			(rej_reason, rej_comment) = claim["rejected"]["reason"].split('|')
	annotation.rejected_statement = rej_statement
	annotation.rejected_statement_reason = rej_reason
	annotation.rejected_statement_comment = rej_comment

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
	#print anns

######################### MAIN ###################################################

def main():
	test()
	

if __name__ == '__main__':
	main()
