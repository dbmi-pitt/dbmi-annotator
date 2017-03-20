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

import sys, uuid, datetime
from sets import Set
from model.Micropublication import *

reload(sys)  
sys.setdefaultencoding('utf8')

######################### QUERY MP Annotation #######################################
## get MP annotations from RDB
# (1) get annotation with claim, (2) append qualifiers based on claimId, (3) add data# (4) add material
# return list of Annotations  
def getMpAnnotations(conn):
	qualifiersD = getQualifiersForClaim(conn) # get qualifiers
	annsD = getMpClaims(conn) # get annotations

	for claimId,ann in annsD.iteritems(): 
		if claimId in qualifiersD:
			qualifiers = qualifiersD[claimId]
			csubject = None; cpredicate = None; cobject = None; cqualifier = None
			for qualifier in qualifiers: # add qualifiers to annotation
				if qualifier.subject:
					ann.csubject = qualifier
				elif qualifier.predicate:
					ann.cpredicate = qualifier
				elif qualifier.object:
					ann.cobject = qualifier
				else:
					ann.cqualifier = qualifier
			addMpDataForAnn(conn, ann, claimId) # add data
			addMpMaterialForAnn(conn, ann, claimId) # add material
		else:
			print "[ERROR] mpEvidenceQry - queryMpAnnotation: no qualifier available for claim (%s) - (%s)" % (ann.source, ann.label)		
	return annsD.values()


def getMpAnnotationByUrn(conn, urn):
	qualifiersD = getQualifiersForClaimClaimByUrn(conn, urn) # get qualifiers
	annD = getMpClaimByUrn(conn, urn) # get annotations

	for claimId,ann in annD.iteritems(): 
		qualifiers = qualifiersD[claimsId]
		csubject = None; cpredicate = None; cobject = None; cqualifier = None
		for qualifier in qualifiers: # add qualifiers to annotation
			if qualifier.subject:
				ann.csubject = qualifier
			elif qualifier.predicate:
				ann.cpredicate = qualifier
			elif qualifier.object:
				ann.cobject = qualifier
			else:
				ann.cqualifier = qualifier

			addMpDataForAnn(conn, ann, claimId) # add data
			addMpMaterialForAnn(conn, ann, claimId) # add material	
	return annsD.values()


######################### QUERY MP Claim ############################################
## query all claim annotation
# param1: psql connection
# return annotations {claimId: Annotation}
def getMpClaims(conn):
	annotations = {} 
	cur = conn.cursor()
	cur.execute("select distinct cann.id, cann.urn, t.has_source, cbody.label, met.entered_value, cann.creator, cann.date_created, s.prefix, s.exact, s.suffix, cann.rejected_statement, cann.rejected_statement_reason, cann.rejected_statement_comment, cann.negation from mp_claim_annotation cann join oa_claim_body cbody on cann.has_body = cbody.id join method met on cann.id = met.mp_claim_id join oa_target t on cann.has_target = t.id join oa_selector s on t.has_selector = s.id;")
		
	for row in cur.fetchall():
		claimId = row[0]
		annotation = createSubAnnotation(row[1], row[2], row[3], row[4], row[5], row[6])
		annotation.date_created = row[6]
		annotation.setOaSelector(row[7], row[8], row[9])
		annotation.setRejected(row[10], row[11], row[12])		
		annotation.negation = row[13]	
		annotations[claimId] = annotation
	return annotations


## query all claim annotation
# param1: psql connection
# param2: annotation urn
# return Annotation {claimId: Annotation}
def getMpClaimByUrn(conn, urn):

	cur = conn.cursor()
	cur.execute("select distinct cann.id, cann.urn, t.has_source, cann.creator, met.entered_value, cbody.label, cann.date_created, s.prefix, s.exact, s.suffix, cann.rejected_statement, cann.rejected_statement_reason, cann.rejected_statement_comment, cann.negation from mp_claim_annotation cann join oa_claim_body cbody on cann.has_body = cbody.id join method met on cann.id = met.mp_claim_id join oa_target t on cann.has_target = t.id join oa_selector s on t.has_selector = s.id where cann.urn = '%s';", urn)
	
	for row in cur.fetchall():
		annotation = Annotation(row[1], row[2], row[3], row[4], row[5])
		annotation.date_created = row[6]
		annotation.setOaSelector(row[7], row[8], row[9])
		annotation.setRejected(row[10], row[11], row[12])		
		annotation.negation = row[13]	
		return {row[0]: annotation}
	return None


## Query all qualifiers
# return Dict {claim_id: Qualifiers List}
def getQualifiersForClaim(conn):
	qDict = {}
	cur = conn.cursor()
	cur.execute("select cann.id, q.subject, q.predicate, q.object, q.qvalue, q.concept_code, q.vocabulary_id, q.qualifier_type_concept_code, q.qualifier_type_vocabulary_id, q.qualifier_role_concept_code, q.qualifier_role_vocabulary_id, q.enantiomer, q.metabolite from qualifier q join mp_claim_annotation cann on q.claim_body_id = cann.has_body;")
	for row in cur.fetchall():
		claimId = row[0]
		qualifier = Qualifier(row[4], row[1], row[2], row[3])
		qualifier.concept_code = row[5]
		qualifier.vocabulary_id = row[6]
		qualifier.qualifier_type_concept_code = row[7]
		qualifier.qualifier_type_vocabulary_id = row[8]
		qualifier.qualifier_role_concept_code = row[9]
		qualifier.qualifier_role_vocabulary_id = row[10]
		qualifier.enantiomer = row[11]
		qualifier.metabolite = row[12]

		if claimId in qDict:
			qDict[claimId].append(qualifier)
		else:
			qDict[claimId] = [qualifier]
	return qDict

## Query all qualifiers
# param1: psql connection
# param2: annotation urn
# return Dict {claim_id: Qualifiers List}
def getQualifiersForClaimByUrn(conn, urn):
	qList = []; claimId = None
	cur = conn.cursor()
	cur.execute("select cann.id, q.subject, q.predicate, q.object, q.qvalue, q.concept_code, q.vocabulary_id, q.qualifier_type_concept_code, q.qualifier_type_vocabulary_id, q.qualifier_role_concept_code, q.qualifier_role_vocabulary_id, q.enantiomer, q.metabolite from qualifier q join mp_claim_annotation cann on q.claim_body_id = cann.has_body where cann.urn = '%s';", urn)
	for row in cur.fetchall():
		claimId = row[0]
		qualifier = Qualifier(row[4], row[1], row[2], row[3])
		qualifier.concept_code = row[5]
		qualifier.vocabulary_id = row[6]
		qualifier.qualifier_type_concept_code = row[7]
		qualifier.qualifier_type_vocabulary_id = row[8]
		qualifier.qualifier_role_concept_code = row[9]
		qualifier.qualifier_role_vocabulary_id = row[10]
		qualifier.enantiomer = row[11]
		qualifier.metabolite = row[12]
		qList.append(qualifier)
	return {claimId: qList}

######################### QUERY MP Data #############################################
## query all data items for claim
# param1: psql connection
# param2: claim id
def queryMpDataByClaimId(conn, claimId):

	qry = """	
	select dann.type, df.data_field_type, df.value_as_string, df.value_as_number, df.value_as_concept_id, s.exact, s.prefix, s.suffix, dann.mp_data_index, dann.ev_supports, met.entered_value, met.inferred_value, eq.question, eq.value_as_string
	from mp_data_annotation dann join oa_data_body dbody on dann.has_body = dbody.id join data_field df on df.data_body_id = dbody.id left join oa_target t on dann.has_target = t.id left join oa_selector s on t.has_selector = s.id join method met on dann.mp_claim_id = met.mp_claim_id and met.mp_data_index = dann.mp_data_index left join evidence_question eq on met.id = eq.method_id
	where dann.mp_claim_id = %s
	""" % (claimId)

	cur = conn.cursor()
	cur.execute(qry)
	return cur.fetchall()


## query data items for claim annotation
# return list of annotation with data items attached
def addMpDataForAnn(conn, annotation, claimId):
	if not isinstance(annotation, Statement):
		dataResults = queryMpDataByClaimId(conn, claimId)

		if isinstance(annotation, ClinicalTrial):
			addClinicalTrialData(annotation, dataResults)
		if isinstance(annotation, PhenotypeClinicalStudy):
			addPhenotypeClinicalStudyData(annotation, dataResults)
		if isinstance(annotation, CaseReport):
			addCaseReportData(annotation, dataResults)


def addClinicalTrialData(annotation, dataResults):
		for row in dataResults:
			dType = row[0] # data type
			dfType = row[1] # data field 
			exact = row[5]; prefix = row[6]; suffix = row[7]; value = str(row[2] or row[3]) # value
			dmIdx = row[8] # data index
			ev_supports = row[9] # EV supports or 		

			if annotation.getSpecificDataMaterial(dmIdx) == None: # create new row for data & material
				dmRow = ClinicalTrialDMRow(dmIdx) 
				addEvRelationship(dmRow, ev_supports)
				annotation.setSpecificDataMaterial(dmRow, dmIdx)
			else: # use existing data & material row 
				dmRow = annotation.getSpecificDataMaterial(dmIdx)

			if dType in ["auc", "cmax" , "clearance", "halflife"]: # add data ratio
				addDataRatioField(dmRow, dType, dfType, value, prefix, exact, suffix)

			question = row[12]; answer = row[13] # add evidence type questions
			addEvidenceTypeQs(dmRow, question, answer)


def addPhenotypeClinicalStudyData(annotation, dataResults):
		for row in dataResults:
			dType = row[0] # data type
			dfType = row[1] # data field 
			exact = row[5]; prefix = row[6]; suffix = row[7]; value = str(row[2] or row[3]) # value
			dmIdx = row[8] # data index
			ev_supports = row[9] # EV supports or 		

			if annotation.getSpecificDataMaterial(dmIdx) == None: # create new row for data & material
				dmRow = PhenotypeDMRow(dmIdx) 
				addEvRelationship(dmRow, ev_supports)
				annotation.setSpecificDataMaterial(dmRow, dmIdx)
			else: # use existing data & material row 
				dmRow = annotation.getSpecificDataMaterial(dmIdx)

			if dType in ["auc", "cmax" , "clearance", "halflife"]: # add data ratio
				addDataRatioField(dmRow, dType, dfType, value, prefix, exact, suffix)

			question = row[12]; answer = row[13] # add evidence type questions
			addEvidenceTypeQs(dmRow, question, answer)


def addCaseReportData(annotation, dataResults):
		for row in dataResults:
			dType = row[0] # data type
			dfType = row[1] # data field 
			exact = row[5]; prefix = row[6]; suffix = row[7]; value = str(row[2] or row[3]) # value
			dmIdx = row[8] # data index
			ev_supports = row[9] # EV supports or 		

			if annotation.getSpecificDataMaterial(dmIdx) == None: # create new row for data & material
				dmRow = CaseReportDMRow(dmIdx) 
				addEvRelationship(dmRow, ev_supports)
				annotation.setSpecificDataMaterial(dmRow, dmIdx)
			else: # use existing data & material row 
				dmRow = annotation.getSpecificDataMaterial(dmIdx)

			if dType == "reviewer":
				addDataReviewerField(dmRow, dType, dfType, value)
			elif dType == "dipsquestion":
				addDataDipsField(dmRow, dType, dfType, value)

			question = row[12]; answer = row[13] # add evidence type questions
			addEvidenceTypeQs(dmRow, question, answer)


def addDataRatioField(dmRow, dType, dfType, value, prefix, exact, suffix):
	if getattr(dmRow, dType): # data ratio exists
		item = getattr(dmRow, dType)
	else: # create new data ratio
		item = DataRatioItem(dType)
		item.setSelector(prefix, exact, suffix)
		setattr(dmRow, dType, item)
	item.setAttribute(dfType, value) # add new attri


def addDataReviewerField(dmRow, dType, dfType, value):
	if getattr(dmRow, dType): 
		item = getattr(dmRow, dType)	
	else:
		item = DataReviewer()
		setattr(dmRow, dType, item)
	item.setAttribute(dfType, value) # add new attri


def addDataDipsField(dmRow, dType, dfType, value):
	if getattr(dmRow, dType):
		item = getattr(dmRow, dType)	
	else:
		item = DataDips()
		setattr(dmRow, "dipsquestion", item)
	dipsDict = item.getDipsDict()
	dipsDict[dfType] = value
	item.setDipsDict(dipsDict) # add new attri


def addEvidenceTypeQs(dmRow, question, answer):
	if question and answer:
		if question == "grouprandom" and not dmRow.grouprandom:
			dmRow.grouprandom = answer
		elif question == "parallelgroup" and not dmRow.parallelgroup:
			dmRow.parallelgroup = answer	


def addEvRelationship(dmRow, ev_supports):
	if dmRow.ev_supports == None and ev_supports != None: # add evidence relationship
		dmRow.ev_supports = ev_supports


######################### QUERY MP Material #########################################
## query material items for claim annotation
# param1: psql connection
# param2: claim id
# return query results
def queryMpMaterialByClaimId(conn, claimId):

	qry = """	
	select mann.type, mf.material_field_type, mf.value_as_string, mf.value_as_number, s.prefix, s.exact, s.suffix, mann.mp_data_index, mann.ev_supports
	from mp_material_annotation mann join oa_material_body mbody on mann.has_body = mbody.id
	join material_field mf on mf.material_body_id = mbody.id
	left join oa_target t on mann.has_target = t.id
	left join oa_selector s on t.has_selector = s.id
	where mann.mp_claim_id = %s
	""" % (claimId)

	cur = conn.cursor()
	cur.execute(qry)
	return cur.fetchall()
	

def addMpMaterialForAnn(conn, annotation, claimId):
	matResults = queryMpMaterialByClaimId(conn, claimId)

	if not isinstance(annotation, Statement):
		if isinstance(annotation, ClinicalTrial):
			addClinicalTrialMaterial(annotation, matResults)
		if isinstance(annotation, PhenotypeClinicalStudy):
			addPhenotypeClinicalStudyMaterial(annotation, matResults)
		if isinstance(annotation, CaseReport):
			addCaseReportMaterial(annotation, matResults)


def addClinicalTrialMaterial(annotation, matResults):

	for row in matResults:

		mType = row[0]  # material type
		mfType = row[1] # material field 
		prefix = row[4]; exact = row[5]; suffix = row[6]; value = str(row[2] or row[3])
		dmIdx = row[7] # data & material index
		ev_supports = row[8] # EV supports or refutes

		if not annotation.getSpecificDataMaterial(dmIdx):
			dmRow = DataMaterialRow(dmIdx) # create new row of data & material
			addEvRelationship(dmRow, ev_supports) # add evidence relationship
			annotation.setSpecificDataMaterial(dmRow, index)
		else:
			dmRow = annotation.getSpecificDataMaterial(dmIdx)

		if mType in ["precipitant_dose","object_dose"]: # add material dose
			addMaterialDoseField(dmRow, mType, mfType, value, prefix, exact, suffix)
		elif mType == "participants":
			addParticipants(dmRow, value, prefix, exact, suffix)


def addPhenotypeClinicalStudyMaterial(annotation, matResults):

	for row in matResults:
		mType = row[0]  # material type
		mfType = row[1] # material field 
		prefix = row[4]; exact = row[5]; suffix = row[6]; value = str(row[2] or row[3])
		dmIdx = row[7] # data & material index
		ev_supports = row[8] # EV supports or refutes

		if not annotation.getSpecificDataMaterial(dmIdx):
			dmRow = DataMaterialRow(dmIdx) # create new row of data & material
			addEvRelationship(dmRow, ev_supports) # add evidence relationship
			annotation.setSpecificDataMaterial(dmRow, index)
		else:
			dmRow = annotation.getSpecificDataMaterial(dmIdx)

		if mType == "participants": 
			addParticipants(dmRow, value, prefix, exact, suffix)
		elif mType == "probesubstrate_dose": 
			addMaterialDoseField(dmRow, mType, mfType, value, prefix, exact, suffix)
		elif mType == "phenotype":
			addPhenotypeField(dmRow, mfType, value, prefix, exact, suffix)


def addCaseReportMaterial(annotation, matResults):

	for row in matResults:

		mType = row[0]  # material type
		mfType = row[1] # material field 
		prefix = row[4]; exact = row[5]; suffix = row[6]; value = str(row[2] or row[3])
		dmIdx = row[7] # data & material index
		ev_supports = row[8] # EV supports or refutes

		if not annotation.getSpecificDataMaterial(dmIdx):
			dmRow = DataMaterialRow(dmIdx) # create new row of data & material
			addEvRelationship(dmRow, ev_supports) # add evidence relationship
			annotation.setSpecificDataMaterial(dmRow, index)
		else:
			dmRow = annotation.getSpecificDataMaterial(dmIdx)

		if mType in ["precipitant_dose","object_dose"]: # add material dose
			addMaterialDoseField(dmRow, mType, mfType, value, prefix, exact, suffix)


def addPhenotypeField(dmRow, mfType, value, prefix, exact, suffix):
	if dmRow.phenotype:
		item = dmRow.phenotype
	else:
		item = MaterialPhenotypeItem()
		item.setSelector(prefix, exact, suffix)
		dmRow.phenotype = item
	item.setAttribute(mfType, value)


def addMaterialDoseField(dmRow, mType, mfType, value, prefix, exact, suffix):
	if getattr(dmRow, mType): # use existing dose if it's available
		doseItem = getattr(dmRow, mType)
	else: # create new dose item 
		doseItem = MaterialDoseItem(mType)
		doseItem.setSelector(prefix, exact, suffix)
		setattr(dmRow, mType, doseItem)
	doseItem.setAttribute(mfType, value)


def addParticipants(dmRow, value, prefix, exact, suffix):
	if not dmRow.participants: # add participants when is not in dmRow yet	
		partItem = MaterialParticipants(value)
		partItem.setSelector(prefix, exact, suffix)
		dmRow.participants = partItem


######################### QUERY Highlight Annotaiton ################################
# query all highlight annotation
# return dict for drug set in document   dict {"doc url": "drug set"} 
def queryHighlightAnns(conn):
	highlightD = {}

	qry = """SELECT h.id, t.has_source, s.exact 
	FROM highlight_annotation h, oa_target t, oa_selector s
	WHERE h.has_target = t.id
	AND t.has_selector = s.id;"""

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():
		source = row[1]; drugname = row[2]
		
		if source in highlightD:		
			highlightD[source].add(drugname)
		else:
			highlightD[source] = Set([drugname])
	return highlightD

#def queryQualifiers()
