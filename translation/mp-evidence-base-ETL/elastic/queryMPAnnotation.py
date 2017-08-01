import sys, csv, json, re, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import datetime, copy
from elasticsearch import Elasticsearch
from sets import Set
from elastic import operations as esop
from model.Micropublication import *
from model.Concept import *
from mapping import tools 

# drugMapD = {} # concept as {"concept name": Concept}
DRUG_MAPPING = "mapping/drug-list-mapped.csv"

## Query and Parse annotations in Elasticsearch #####################################
def getMPAnnsByBody(es_host, es_port, query_condit, pgconn):
	## query condition (refers to elasticsearch REST API)
	body = {'query': { 'term': {'annotationType': 'MP'}}}
	if query_condit:
		body = query_condit
	res = esop.queryByBody(es_host, es_port, body)	
	print "Elasticsearch get MP annotations (%s)" % res['hits']['total']
	return parseToMPAnns(res['hits']['hits'], pgconn)


def getMPAnnById(es_host, es_port, annId, pgconn):
	res = esop.queryById(es_host, es_port, annId)	
	ann = parseToMPAnn(res, pgconn)
	return ann


def parseToMPAnns(documents, pgconn):

	anns = []
	for doc in documents:
		ann = parseToMPAnn(doc, pgconn)
		if ann:
			anns.append(ann)
	return anns

# parse JSON document, applying omop vocabulary for standardize concepts
# return object Annotation based on method of annotation
def parseToMPAnn(document, pgconn):
        drugMapD = tools.getDrugMappingDict(DRUG_MAPPING, pgconn)
        
	doc = document["_source"]; doc_urn = document["_id"]
	method = doc["argues"]["method"]; annotation = None

	if method == "DDI clinical trial":
		annotation = createClinicalTrial(doc, doc_urn, drugMapD)
	elif method == "Statement":
		annotation = createStatement(doc, doc_urn, drugMapD)
	elif method == "Phenotype clinical study":
		annotation = createPhenotypeClinicalStudy(doc, doc_urn, drugMapD)
	elif method == "Case Report":
		annotation = createCaseReport(doc, doc_urn, drugMapD)
	return annotation


# add OMOP concept code and vocabulary id to qualifier
def addQualifierConcept(qualifier, drugMapD):
        if not qualifier or not qualifier.qvalue or not drugMapD:
                #print "[ERROR] queryMPAnnotation.py: concept code mapping not availiable"
                return
        
	if qualifier.qvalue.lower() in drugMapD:
		concept = drugMapD[qualifier.qvalue.lower()]
		qualifier.setQualifierConcept(concept.concept_code, concept.vocabulary_id)


## STATEMENT ########################################################################
## initial statement annotation
# param1: annotation in Json from elasticsearch
# param2: annotation Id
# return: Statement annotation
def createStatement(doc, doc_urn, drugMapD):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	label = claim["label"]; method = doc["argues"]["method"]; date = doc["created"]
	exact = getSelectorTxt(claim, "exact"); prefix = getSelectorTxt(claim, "prefix"); suffix = getSelectorTxt(claim, "suffix")
	qualifier = claim["qualifiedBy"];

        negation = "No"
        if "negation" in claim:
                negation = claim["negation"]
        else:
                print "[WARN] doc (%s) statement (%s), negation is undefined" % (source, label)
	drugname1 = qualifier["drug1"].replace(".",""); drugname2 = qualifier["drug2"].replace(".",""); enzyme = qualifier["enzyme"]; predicate = qualifier["relationship"]; precipitant = qualifier["precipitant"]

	if not validateStatement(precipitant, drugname1, drugname2, enzyme, predicate, source, label):
		return None

	## MP Claim
	annotation = createSubAnnotation(doc_urn, source, label, method, email, date)
	addQualifiersForST(annotation, drugname1, drugname2, predicate, enzyme, precipitant, parseDrugPC("drug1PC", qualifier), parseDrugPC("drug2PC", qualifier), drugMapD)
	annotation.setOaSelector(prefix, exact, suffix)
	addRejected(annotation, claim)
	annotation.negation = negation # negate this statement

	return annotation


## add qualifiers to Statement annotation
# parma1: annotation obj
# param2: drug1 name
# param3: drug2 name
# param4: DDI relationship
# param5: enzyme
# param6: precipitant in DDI
# param7: drug1 parent compound
# param8: drug2 parent compound
def addQualifiersForST(annotation, drugname1, drugname2, predicate, enzyme, precipitant, drug1PC, drug2PC, drugMapD):
	csubject = None; cobject = None

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

	elif predicate in ["inhibits", "substrate of"]:
		csubject = Qualifier(drugname1, True, False, False) # drug1 as mpsubject/precipitant
		csubject.setRolePrecipitant()
		csubject.setTypeDrugProduct()
		addParentCompound(csubject, drug1PC)				

		cobject = Qualifier(enzyme, False, False, True) # enzyme as mpobject
		cobject.setTypeEnzyme()
		cobject.setRoleObject()

	addQualifierConcept(csubject, drugMapD)
	addQualifierConcept(cobject, drugMapD)
		
	cpredicate = Qualifier(predicate, False, True, False)
	annotation.setQualifiers(csubject, cpredicate, cobject)


## DDI CLINICAL TRIAL ###############################################################
## initial clinical trial annotation
# param1: annotation in Json from elasticsearch
# param2: annotation Id
# return: Clinical trial annotation
def createClinicalTrial(doc, doc_urn, drugMapD):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	if not validateClinicalTrial(claim, source):
		return None

	label = claim["label"]; method = doc["argues"]["method"]; date = doc["created"]
	exact = getSelectorTxt(claim, "exact"); prefix = getSelectorTxt(claim, "prefix"); suffix = getSelectorTxt(claim, "suffix")
	qualifier = claim["qualifiedBy"]; 
	drugname1 = qualifier["drug1"].replace(".",""); drugname2 = qualifier["drug2"].replace(".",""); predicate = qualifier["relationship"]; precipitant = qualifier["precipitant"]
        enzyme = None
        if "enzyme" in qualifier:
                qualifier["enzyme"]

	## MP Claim
	annotation = createSubAnnotation(doc_urn, source, label, method, email, date)
	addQualifiersForCT(annotation, drugname1, drugname2, predicate, enzyme, precipitant, parseDrugPC("drug1PC", qualifier), parseDrugPC("drug2PC", qualifier), drugMapD)
	annotation.setOaSelector(prefix, exact, suffix)
	addRejected(annotation, claim)

	## MP Data
	dataL = claim["supportsBy"]
	if dataL and len(dataL) > 0:
		for i in xrange(0, len(dataL)):
			data = dataL[i]
                        if not validateClinicalTrialDataMaterial(data, doc["rawurl"], doc["email"], doc["created"], claim["label"]):
                                return None
                                
			dmRow = ClinicalTrialDMRow(i)
			dmRow.ev_supports = parseEvSupports(data["evRelationship"]) 
			addEVTypeQuestions(dmRow, data) # add evidence type question 
			for ratioType in ["auc", "cmax", "clearance", "halflife"]:
				if data[ratioType]:
					ratioItem = createDataRatioItem(data[ratioType], ratioType)	
					setattr(dmRow, ratioType, ratioItem)
 
			material = data["supportsBy"]["supportsBy"]
			if material:
				if material["participants"]:
					dmRow.participants = createParticipantsItem(material["participants"])

				cprecipitant = annotation.getPrecipitantQualifier()
				cobject = annotation.getObjectQualifier()
				if material["drug1Dose"]:
					if drugname1 == cprecipitant.qvalue: ## drug1 is precipitant
						dmRow.precipitant_dose = createDoseItem(material["drug1Dose"], "precipitant", drugname1)
					elif drugname1 == cobject.qvalue: ## drug1 is object
						dmRow.object_dose = createDoseItem(material["drug1Dose"], "object", drugname1)
				if material["drug2Dose"]:
					if drugname2 == cprecipitant.qvalue: ## drug2 is precipitant
						dmRow.precipitant_dose = createDoseItem(material["drug2Dose"], "precipitant", drugname2)
					elif drugname2 == cobject.qvalue: ## drug2 is object
						dmRow.object_dose = createDoseItem(material["drug2Dose"], "object", drugname2)
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
def addQualifiersForCT(annotation, drugname1, drugname2, predicate, enzyme, precipitant, drug1PC, drug2PC, drugMapD):
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
		
	addQualifierConcept(csubject, drugMapD)
	addQualifierConcept(cobject, drugMapD)
	if cqualifier:
		addQualifierConcept(cqualifier, drugMapD)

	cpredicate = Qualifier(predicate, False, True, False)
	annotation.setQualifiers(csubject, cpredicate, cobject, cqualifier)


## PHENOTYPE CLINICAL STUDY ###############################################################
## initial phenotype clinical study annotation
# param1: annotation in Json from elasticsearch
# param2: annotation Id
# return: Phenotype clinical study annotation
def createPhenotypeClinicalStudy(doc, doc_urn, drugMapD):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	label = claim["label"]; method = doc["argues"]["method"]; date = doc["created"]
	exact = getSelectorTxt(claim, "exact"); prefix = getSelectorTxt(claim, "prefix"); suffix = getSelectorTxt(claim, "suffix")
	qualifier = claim["qualifiedBy"]
	drugname1 = qualifier["drug1"].replace(".",""); enzyme = qualifier["enzyme"]; predicate = qualifier["relationship"];

	if not validatePhenotypeClinicalStudy(drugname1, enzyme, predicate, source, label):
		return None

	## MP Claim
	annotation = createSubAnnotation(doc_urn, source, label, method, email, date)
	addQualifiersForPH(annotation, drugname1, predicate, enzyme, parseDrugPC("drug1PC", qualifier), drugMapD)
	annotation.setOaSelector(prefix, exact, suffix)
	addRejected(annotation, claim)

	## MP Data
	dataL = claim["supportsBy"]
	if dataL and len(dataL) > 0:
		for i in xrange(0, len(dataL)):
			data = dataL[i]
			dmRow = PhenotypeDMRow(i)
			dmRow.ev_supports = parseEvSupports(data["evRelationship"]) 
			addEVTypeQuestions(dmRow, data) # add evidence type question 
			for ratioType in ["auc", "cmax", "clearance", "halflife"]:
				if data[ratioType]:
					ratioItem = createDataRatioItem(data[ratioType], ratioType)	
					setattr(dmRow, ratioType, ratioItem)
 
			material = data["supportsBy"]["supportsBy"]
			if material:
				if material["participants"]:
					dmRow.participants = createParticipantsItem(material["participants"])
				if material["drug1Dose"]:
					dmRow.probesubstrate_dose = createDoseItem(material["drug1Dose"], "probesubstrate", drugname1)
				if material["phenotype"]:
					dmRow.phenotype = createPhenotypeItem(material["phenotype"])

			annotation.setSpecificDataMaterial(dmRow, i) # add new row of data and material		
	return annotation


## add qualifiers to Phenotype clinical study annotation
# parma1: annotation obj
# param2: drug1 name
# param3: DDI relationship
# param4: enzyme
# param5: drug1 parent compound
def addQualifiersForPH(annotation, drugname1, predicate, enzyme, drug1PC, drugMapD):

	csubject = Qualifier(drugname1, True, False, False) # drug1 as mpsubject/precipitant
	csubject.setTypeDrugProduct()
	csubject.setRoleProbeSubstrate()
	addParentCompound(csubject, drug1PC)				

	cobject = Qualifier(enzyme, False, False, True) # enzyme as mpobject
	cobject.setTypeEnzyme()
	cobject.setRoleObject()
					
	addQualifierConcept(csubject, drugMapD)
	addQualifierConcept(cobject, drugMapD)

	cpredicate = Qualifier(predicate, False, True, False)
	annotation.setQualifiers(csubject, cpredicate, cobject)


## CASE REPORT ######################################################################
## initial case report annotation
# param1: annotation in Json from elasticsearch
# param2: annotation Id
# return: Case report annotation
def createCaseReport(doc, doc_urn, drugMapD):

	claim = doc["argues"]; source = doc["rawurl"]; email = doc["email"]
	label = claim["label"]; method = doc["argues"]["method"]; date = doc["created"]
	if not validateCaseReport(claim, source):
		return None

	exact = getSelectorTxt(claim, "exact"); prefix = getSelectorTxt(claim, "prefix"); suffix = getSelectorTxt(claim, "suffix")
	qualifier = claim["qualifiedBy"]; precipitant = qualifier["precipitant"]
	drugname1 = qualifier["drug1"].replace(".",""); drugname2 = qualifier["drug2"].replace(".",""); predicate = qualifier["relationship"];

	## MP Claim
	annotation = createSubAnnotation(doc_urn, source, label, method, email, date)
	addQualifiersForCR(annotation, drugname1, predicate, drugname2, precipitant, parseDrugPC("drug1PC", qualifier), parseDrugPC("drug2PC", qualifier), drugMapD)
	annotation.setOaSelector(prefix, exact, suffix)
	addRejected(annotation, claim)

	## MP Data
	dataL = claim["supportsBy"]
	if dataL and len(dataL) > 0:
		for i in xrange(0, len(dataL)):
			data = dataL[i]
			dmRow = CaseReportDMRow(i)
			if data["dips"]:
				dmRow.dipsquestion = createDipsItem(data["dips"])
			if data["reviewer"]:
				dmRow.reviewer = createReviewer(data["reviewer"])
 
			material = data["supportsBy"]["supportsBy"]
			if material:
				cprecipitant = annotation.getPrecipitantQualifier()
				cobject = annotation.getObjectQualifier()
				if material["drug1Dose"]:
					if drugname1 == cprecipitant.qvalue: ## drug1 is precipitant
						dmRow.precipitant_dose = createDoseItem(material["drug1Dose"], "precipitant", drugname1)
					elif drugname1 == cobject.qvalue: ## drug1 is object
						dmRow.object_dose = createDoseItem(material["drug1Dose"], "object", drugname1)
				if material["drug2Dose"]:
					if drugname2 == cprecipitant.qvalue: ## drug2 is precipitant
						dmRow.precipitant_dose = createDoseItem(material["drug2Dose"], "precipitant", drugname2)
					elif drugname2 == cobject.qvalue: ## drug2 is object
						dmRow.object_dose = createDoseItem(material["drug2Dose"], "object", drugname2)
			annotation.setSpecificDataMaterial(dmRow, i) # add new row of data and material		
	return annotation


## add qualifiers to Case report annotation
# parma1: annotation obj
# param2: drug1 name
# param3: DDI relationship
# param4: drug2 name
# param5: precipitant role in DDI
# param6: drug1 parent compound
# param7: drug2 parent compound
def addQualifiersForCR(annotation, drugname1, predicate, drugname2, precipitant, drug1PC, drug2PC, drugMapD):
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

	addQualifierConcept(csubject, drugMapD)
	addQualifierConcept(cobject, drugMapD)

	cpredicate = Qualifier(predicate, False, True, False)
	annotation.setQualifiers(csubject, cpredicate, cobject)


## Add attributes to annotation #####################################################
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


def createPhenotypeItem(item):
	phItem = MaterialPhenotypeItem()
	exact = getSelectorTxt(item, "exact"); prefix = getSelectorTxt(item, "prefix"); suffix = getSelectorTxt(item, "suffix")
	phItem.setSelector(prefix, exact, suffix)
	phItem.ptype = item["type"]
	phItem.value = item["typeVal"]
	if "metabolizer" in item:
		phItem.metabolizer = item["metabolizer"]
        if "population" in item:
	        phItem.population = item["population"]
	return phItem


def createReviewer(dataRev):
	revItem = DataReviewer()
	revItem.reviewer = dataRev["reviewer"]
	revItem.date = dataRev["date"]
	revItem.total = dataRev["total"]
	revItem.lackinfo = dataRev["lackInfo"]
	return revItem


def createDipsItem(dataDips):
	dipsItem = DataDips()
	dipsD = {}
	for qs in dataDips:
		dipsD[qs] = dataDips[qs]
	dipsItem.setDipsDict(dipsD)
	return dipsItem


## add parent compound to qualifier		
# param1: Qualifier
# param2: drugPC string from AnnotationPress "enantiomer|metabolite"
def addParentCompound(qualifier, drugPC):
	if drugPC and "|" in drugPC:
		pcL = drugPC.split("|") 
		[enantiomer, metabolite] = [isPC(pcL[0]), isPC(pcL[1])]
		qualifier.enantiomer = enantiomer
		qualifier.metabolite = metabolite
	else:
		qualifier.enantiomer = False
		qualifier.metabolite = False


## convert parent compound from string in AnnotationPress to boolean for Annotation
# param1: "enantiomer|metabolite"
# return: boolean for "enantiomer", "metabolite"
def isPC(pcStr):
	if pcStr in ["enantiomer", "metabolite"]:
		return True
	else:
		return False

	
def addRejected(annotation, claim):
	# ## statement rejection 
	rej_statement = False; rej_reason = None; rej_comment = None
	if "rejected" in claim:
		if claim["rejected"]["reason"]:
			rej_statement = True
			if '|' in claim["rejected"]["reason"]:
				(rej_reason, rej_comment) = claim["rejected"]["reason"].split('|')
	annotation.rejected_statement = rej_statement
	annotation.rejected_statement_reason = rej_reason
	annotation.rejected_statement_comment = rej_comment


def addEVTypeQuestions(dmRow, data):
	if "grouprandom" in data and data["grouprandom"]:
		if data["grouprandom"] == "yes":
			dmRow.grouprandom = "yes"
		elif data["grouprandom"] == "no":
			dmRow.grouprandom = "no"			
	if "parallelgroup" in data and data["parallelgroup"]:
		if data["parallelgroup"] == "yes":
			dmRow.parallelgroup = "yes"
		elif data["parallelgroup"] == "no":
			dmRow.parallelgroup = "no"

	
## Validate Claim ##########################################################################
def validateStatement(precipitant, drugname1, drugname2, enzyme, predicate, source, label):
	## data validation
	if ((predicate == "interact with" and (not drugname1 or not drugname2 or enzyme)) or (predicate in ["inhibits", "substrate of"] and (not drugname1 or not enzyme or drugname2))): 
		print "[WARN] Statement: qualifier error, skip (%s) - (%s)" % (source, label)
		return False
	return True


def validateClinicalTrial(claim, source):
	label = claim["label"]; qualifier = claim["qualifiedBy"]; predicate = qualifier["relationship"]

	## validate precipitant
	if "precipitant" not in qualifier or qualifier["precipitant"] not in ["drug1", "drug2"]:
		print "[ERROR] createClinicalTrial: percipitant undefined, skip source (%s), claim (%s)" % (source, label)
		return False
	## claim validation
	if ((predicate == "interact with" and (not qualifier["drug1"] or not qualifier["drug2"])) or (predicate in ["inhibits", "substrate of"] and (not qualifier["drug1"] or not qualifier["drug2"] or not qualifier["enzyme"]))): 
		print "[WARN] DDI clinical trial: qualifier error, skip (%s) - (%s)" % (source, label)
		return False
        
	return True

def validatePhenotypeClinicalStudy(drugname1, enzyme, predicate, source, label):
	if not drugname1 or not enzyme:
		print "[ERROR] createPhenotypeClinicalStudy: drug or enzyme undefined, skip source (%s), claim (%s)" % (source, label)
		return False
	if predicate not in ["inhibits", "substrate of"]:
		print "[ERROR] createPhenotypeClinicalStudy: relationship undefined, skip source (%s), claim (%s)" % (source, label)
		return False
	return True

def validateCaseReport(claim, source):
	label = claim["label"]; qualifier = claim["qualifiedBy"]

	## validate precipitant
	if ("precipitant" not in qualifier or not qualifier["precipitant"]) or qualifier["precipitant"] not in ["drug1", "drug2"]:
		print "[ERROR] createCaseReport: percipitant undefined, skip source (%s), claim (%s)" % (source, label)
		return False
	## data validation
	if ("relationship" not in qualifier or qualifier["relationship"] != "interact with" or (not qualifier["drug1"] or not qualifier["drug2"])):
		print "[WARN] Case Report: qualifier error, skip (%s) - (%s)" % (source, label)
		return False
	return True


## Validate Data & Material #########################################################
def validateClinicalTrialDataMaterial(data, rawurl, email, dateCreated, label):
        if "evRelationship" not in data:
                print "[ERROR] createClinicalTrial: evRelationship undified, skip source (%s), claim(%s), author(%s), date(%s)" % (rawurl, label, email, dateCreated)
                return False
        return True


## Utils ############################################################################
def parseEvSupports(evRelationship):
	if evRelationship == "supports":
		return True
	elif evRelationship in ["refutes", "challenges"]:
		return False
	return True


def parseDrugPC(drugIdxPC, qualifier):
	if drugIdxPC in qualifier:		
		return qualifier[drugIdxPC]
	else:
		return None


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


def test():
	query_condit = {'query': { 'term': {'annotationType': 'MP'}}}
	anns = getMPAnnsByBody("localhost", "9200", query_condit)
	#print anns

######################### MAIN ###################################################

def main():
	test()
	

if __name__ == '__main__':
	main()
	#DRUG_MAPPING = "./../mapping/drug-list-mapped.csv"
	#tools.printMapping(DRUG_MAPPING)
