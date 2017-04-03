import sys, csv, json, re, os
import uuid
import datetime, copy
from elasticsearch import Elasticsearch
from elastic import operations as esop
from sets import Set


def queryDictAnnsById(host, port, annotationId):
	res = esop.queryById(host, port, annotationId)
	annsL = parseAnnotation(res)
	return annsL

def queryDictAnnsByBody(es_host, es_port, query_condit):
	## query condition (refers to elasticsearch REST API)
	doc = {'query': { 'term': {'annotationType': 'MP'}}}
	if query_condit:
		doc = query_condit

	res = esop.queryByBody(es_host, es_port, doc)	
	annsL = parseAnnotations(res['hits']['hits'])

	return annsL


def parseAnnotations(annotations):
	annsL = []
	for annotation in annotations:
		annsL.extend(parseAnnotation(annotation))
	return annsL


def parseAnnotation(annotation):
	annsL = []
	
	ann = annotation["_source"]
	initDict= getAnnDict()
	initDict["id"] = annotation["_id"]
	initDict["document"] = ann["rawurl"]
	initDict["useremail"] = ann["email"]
	
	claim = ann["argues"]
	initDict["claimlabel"] = claim["label"]
	initDict["claimtext"] = claim["hasTarget"]["hasSelector"]["exact"]
	initDict["method"] = claim["method"]	
	
	initDict["relationship"] = claim["qualifiedBy"]["relationship"]

	## drug 1 (required) and drug 2
	initDict["drug1"] = claim["qualifiedBy"]["drug1"]
	if "drug2" in claim["qualifiedBy"]:
		initDict["drug2"] = claim["qualifiedBy"]["drug2"]
	
	if "enzyme" in claim["qualifiedBy"]:
		initDict["enzyme"] = claim["qualifiedBy"]["enzyme"]

	if "precipitant" in claim["qualifiedBy"]:
		initDict["precipitant"] = claim["qualifiedBy"]["precipitant"]

	## parent coumpound
	if "drug1PC" in claim["qualifiedBy"]:
		initDict["drug1PC"] = claim["qualifiedBy"]["drug1PC"]

	if "drug2PC" in claim["qualifiedBy"]:
		initDict["drug2PC"] = claim["qualifiedBy"]["drug2PC"]

	if "rejected" in claim and claim["rejected"]:			
		initDict["rejected"] = claim["rejected"]["reason"] or ""

	dataL = claim["supportsBy"]

	## parse data & material
	if len(dataL) > 0:
		for data in dataL:

			annDict = copy.deepcopy(initDict)

			material = data["supportsBy"]["supportsBy"]
			annDict = addDataMaterialToAnnDict(data, material, annDict)
			annsL.append(annDict)
	else:
		annsL.append(initDict)

	return annsL

def addDataMaterialToAnnDict(data, material, annDict):
	## parse data
	if "evRelationship" in data:
		annDict["evRelationship"] = data["evRelationship"] or ""

	for field in ["auc","cmax","clearance","halflife"]:
		if data[field]:						
			annDict[field+"value"] = data[field]["value"]
			annDict[field+"type"] = data[field]["type"]
			annDict[field+"direction"] = data[field]["direction"]
			annDict[field+"text"] = getTextSpan(data[field])

	if data["dips"]:
		dipsQsStr = ""
		qsL=["q1","q2","q3","q4","q5","q6","q7","q8","q9","q10"]
		for q in qsL:
			if q in data["dips"]:
				if (q == len(qsL) - 1):
					dipsQsStr += data["dips"][q]
				else:
					dipsQsStr += data["dips"][q] + "|"				
		annDict["dipsquestion"] = dipsQsStr

	if "reviewer" in data and data["reviewer"]:

		annDict["reviewer"] = data["reviewer"]["reviewer"] or ""
		annDict["reviewerdate"] = data["reviewer"]["date"] or ""
		annDict["reviewertotal"] = data["reviewer"]["total"] or ""
		annDict["reviewerlackinfo"] = data["reviewer"]["lackInfo"]

	if "grouprandom" in data and data["grouprandom"]:
		annDict["grouprandom"] = data["grouprandom"] or ""
						
	if "parallelgroup" in data and data["parallelgroup"]:
		annDict["parallelgroup"] = data["parallelgroup"] or ""
							
	## parse material
	if material["participants"]:
		annDict["participants"] = material["participants"]["value"]			
		annDict["participantstext"] = getTextSpan(material["participants"])
	if material["drug1Dose"]:
		annDict["drug1dose"] = material["drug1Dose"]["value"] or ""
		annDict["drug1formulation"] = material["drug1Dose"]["formulation"] or ""
		annDict["drug1duration"] = material["drug1Dose"]["duration"] or ""
		annDict["drug1regimens"] = material["drug1Dose"]["regimens"] or ""
		annDict["drug1dosetext"] = getTextSpan(material["drug1Dose"])

	if material["drug2Dose"]:
		annDict["drug2dose"] = material["drug2Dose"]["value"] or ""
		annDict["drug2formulation"] = material["drug2Dose"]["formulation"] or ""
		annDict["drug2duration"] = material["drug2Dose"]["duration"] or ""
		annDict["drug2regimens"] = material["drug2Dose"]["regimens"] or ""
		annDict["drug2dosetext"] = getTextSpan(material["drug2Dose"])

	if material["phenotype"]:
		annDict["phenotypetype"] = material["phenotype"]["type"] or ""
		annDict["phenotypevalue"] = material["phenotype"]["typeVal"] or ""
		if "metabolizer" in material["phenotype"] and "population" in material["phenotype"]:
			annDict["phenotypemetabolizer"] = material["phenotype"]["metabolizer"] or ""
			annDict["phenotypepopulation"] = material["phenotype"]["population"] or ""

	return annDict

def getAnnDict():
	return {"document": None, "useremail": None, "claimlabel": None, "claimtext": None, "method": None, "relationship": None, "drug1": None, "drug2": None, "drug1PC": None, "drug2PC": None, "precipitant": None, "enzyme": None, "rejected": None, "evRelationship":None, "participants":None, "participantstext":None, "drug1dose":None, "drug1formulation":None, "drug1duration":None, "drug1regimens":None, "drug1dosetext":None, "drug2dose":None, "phenotypetype": None, "phenotypevalue": None, "phenotypemetabolizer": None, "phenotypepopulation": None, "drug2formulation":None, "drug2duration":None, "drug2regimens":None, "drug2dosetext":None, "aucvalue":None, "auctype":None, "aucdirection":None, "auctext":None, "cmaxvalue":None, "cmaxtype":None, "cmaxdirection":None, "cmaxtext":None, "clearancevalue":None, "clearancetype":None, "clearancedirection":None, "clearancetext":None, "halflifevalue":None, "halflifetype":None, "halflifedirection":None, "halflifetext":None, "dipsquestion":None, "reviewer":None, "reviewerdate":None, "reviewertotal":None, "reviewerlackinfo":None, "grouprandom":None, "parallelgroup":None, "id": None}


def getTextSpan(field):
	if field["hasTarget"]:
		if field["hasTarget"]["hasSelector"]:
			return field["hasTarget"]["hasSelector"]["exact"]
	return ""


######################### MAIN ##########################

def main():
	print query()
	


if __name__ == '__main__':
	main()
