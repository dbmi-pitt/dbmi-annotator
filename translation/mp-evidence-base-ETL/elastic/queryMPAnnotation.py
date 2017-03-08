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
		anns.append(ann)
	return anns

def parseToMPAnn(document):
	doc = document["_source"]; doc_urn = document["_id"]
	method = doc["argues"]["method"];
	annotation = None

	if method == "DDI clinical trial":
		annotation = createClinicalTrial(doc, doc_urn)

	return annotation


## initial clinical trial annotation
# param1: drug1 name
# param2: drug2 name
# param3: DDI relationship
# param4: enzyme
# param5: precipitant in DDI
# param6: drug1 parent compound
# param7: drug2 parent compound
# return: ClinicalTrial
def createClinicalTrial(doc, doc_urn):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	label = claim["label"]
	exact = getSelectorTxt(claim, "exact"); prefix = getSelectorTxt(claim, "prefix"); suffix = getSelectorTxt(claim, "suffix")

	qualifier = claim["qualifiedBy"]; 
	drugname1 = qualifier["drug1"]; drugname2 = qualifier["drug2"]; enzyme = qualifier["enzyme"]; predicate = qualifier["relationship"]; precipitant = qualifier["precipitant"]
	drug1PC = qualifier["drug1PC"]; drug2PC = qualifier["drug2PC"]

	## data validation
	if precipitant not in ["drug1","drug2"] or ((predicate == "interact with" and (not drugname1 or not drugname2 or enzyme)) or (predicate in ["inhibits", "substrate of"] and (not drugname1 or not drugname2 or not enzyme))): 
		print "[WARN] DDI clinical trial: qualifier error, skip (%s) - (%s)" % (source, label)
		return
	
	cpredicate = Qualifier(predicate, False, True, False)
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
		
	annotation = ClinicalTrial()
	annotation.setOaSelector(prefix, exact, suffix)
	annotation.setQualifiers(csubject, cpredicate, cobject, cqualifier)
	return annotation

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
