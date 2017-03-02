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
from model.micropublication import Annotation, DataMaterialRow, DMItem, DataRatioItem, MaterialDoseItem, MaterialParticipants, MaterialPhenotypeItem, DataReviewer, DataDips

######################### QUERY MP Annotation ##########################
# query all mp annotations
# return annotations with claim, data and material
def queryAllMpAnnotation(conn):
	mpAnnotations = []
	claimAnns = queryAllMpClaim(conn)

	for claimId,claimAnn in claimAnns.items():

		claimDataAnno = queryMpData(conn, claimAnn, claimId)
		claimDataMatAnno = queryMpMaterial(conn, claimDataAnno, claimId)

		mpAnnotations.append(claimDataMatAnno)
	return mpAnnotations


# query all mp annotations
# return annotations with claim, data and material
def queryMpAnnotationByUrn(conn, annotationUrn):
	claimAnn = queryMpClaimByUrn(conn, annotationUrn)
	claimDataAnn = queryMpData(conn, claimAnn, claimAnn.claimid)
	claimDataMatAnn = queryMpMaterial(conn, claimDataAnn, claimAnn.claimid)

	return claimDataMatAnn

######################### QUERY MP Claim ##########################
## query all claim annotation by document URL
## return {{key: id-1, value: Ann-1"}, {key: id-2, value: Ann-2"}, ...}
def queryAllMpClaim(conn):
	annotations = {} # key: id, value obj Annotation
	cur = conn.cursor()

	qry = """
	select cann.id, t.has_source, cann.creator, cann.date_created, s.exact, s.prefix, s.suffix, cbody.label, qualifierrole(q.subject, q.predicate, q.object) as qtype, qvalue, cann.rejected_statement, cann.rejected_statement_reason, cann.rejected_statement_comment, met.entered_value, cann.negation 
	from mp_claim_annotation cann join oa_claim_body cbody on cann.has_body = cbody.id
	join qualifier q on cbody.id = q.claim_body_id
	join method met on cann.id = met.mp_claim_id 
	join oa_target t on cann.has_target = t.id
	join oa_selector s on t.has_selector = s.id;
	"""
	cur.execute(qry)
		
	for row in cur.fetchall():
		id = row[0]
		if id not in annotations: ## Using existing annotation if it's available
			annotation = Annotation()
			annotations[id] = annotation
		else:
			annotation = annotations[id]

		## claim qualifiers
		if row[8] == "subject":
			annotation.csubject = row[9]
		elif row[8] == "predicate":
			annotation.cpredicate = row[9]
		elif row[8] == "object":
			annotation.cobject = row[9]
		elif row[8] == "enzyme":
			annotation.cenzyme = row[9]
		else:
			print "[ERROR] qualifier role unidentified qvalue: %s (claimid %s)" % (row[8], id) 

		## claim source and label
		if annotation.source == None:
			annotation.source = row[1]
		if annotation.label == None:
			annotation.label = row[7]

		## claim text selector
		if annotation.exact == None:
			annotation.setOaSelector(row[5], row[4], row[6])

		## user entered method
		if annotation.method == None:
			annotation.method = row[13]

		## assertion negation 
		if annotation.negation == None and row[14] != None:
			annotation.negation = row[14]

		## rejected reason
		if annotation.rejected == None and row[10] == True:
			annotation.rejected = row[11] + "|" + row[12]			

	return annotations


def queryMpClaimUrn(conn, urn):
	"""
	query claim annotation by annotationId
	return Annotation
	"""
	cur = conn.cursor()

	qry = """
	select cann.id, t.has_source, cann.creator, cann.date_created, s.exact, s.prefix, s.suffix, cbody.label, qualifierrole(q.subject, q.predicate, q.object) as qtype, qvalue, cann.rejected_statement, cann.rejected_statement_reason, cann.rejected_statement_comment, met.entered_value, cann.negation 
	from mp_claim_annotation cann join oa_claim_body cbody on cann.has_body = cbody.id
	join qualifier q on cbody.id = q.claim_body_id
	join method met on cann.id = met.mp_claim_id 
	join oa_target t on cann.has_target = t.id
	join oa_selector s on t.has_selector = s.id
	where cann.urn = '%s';   """ % (urn)
	cur.execute(qry)		

	annotation = Annotation()
	for row in cur.fetchall():

		annotation.claimid = row[0]
		annotation.urn = urn
		
		## claim qualifiers
		if row[8] == "subject":
			annotation.csubject = row[9]
		elif row[8] == "predicate":
			annotation.cpredicate = row[9]
		elif row[8] == "object":
			annotation.cobject = row[9]
		elif row[8] == "enzyme":
			annotation.cenzyme = row[9]
		else:
			print "[ERROR] qualifier role unidentified qvalue: %s (claimid %s)" % (row[8], annotation.claimid) 

		## claim source and label
		if annotation.source == None:
			annotation.source = row[1]
		if annotation.label == None:
			annotation.label = row[7]

		## claim text selector
		if annotation.exact == None:
			annotation.setOaSelector(row[5], row[4], row[6])

		## user entered method
		if annotation.method == None:
			annotation.method = row[13]

		## assertion negation 
		if annotation.negation == None and row[14] != None:
			annotation.negation = row[14]

		## rejected reason
		if annotation.rejected == None and row[10] == True:
			annotation.rejected = row[11] + "|" + row[12]		

	return annotation

		
######################### QUERY MP Data ##########################
# query data items for claim annotation
# return list of annotation with data items attached
def queryMpData(conn, annotation, claimid):

	qry = """	
	select dann.type, df.data_field_type, df.value_as_string, df.value_as_number, s.exact, s.prefix, s.suffix, dann.mp_data_index, dann.ev_supports, dann.rejected, dann.rejected_reason, dann.rejected_comment, met.entered_value, met.inferred_value, eq.question, eq.value_as_string
	from mp_data_annotation dann 
	join oa_data_body dbody on dann.has_body = dbody.id 
	join data_field df on df.data_body_id = dbody.id 
	left join oa_target t on dann.has_target = t.id
	left join oa_selector s on t.has_selector = s.id
	join method met on dann.mp_claim_id = met.mp_claim_id and met.mp_data_index = dann.mp_data_index
	left join evidence_question eq on met.id = eq.method_id
	where dann.mp_claim_id = %s
	""" % (claimid)

	cur = conn.cursor()
	cur.execute(qry)
		
	for row in cur.fetchall():

		dType = row[0]  # data type
		dfType = row[1] # data field 
		exact = row[4]; value = str(row[2] or row[3]) # value as string or number
		index = row[7] # data index
		evRelationship = row[8] # EV supports or refutes
		dmRow = None

		if annotation.getSpecificDataMaterial(index) == None:
			dmRow = DataMaterialRow() # create new row of data & material
			annotation.setSpecificDataMaterial(dmRow, index)
		else: # current row of data & material exists 
			dmRow = annotation.getSpecificDataMaterial(index)

		if dType in ["auc", "cmax" , "clearance", "halflife"]:
			if dmRow.getDataRatioItemInRow(dType): # DataRatioItem exists
				dataRatioItem = dmRow.getDataRatioItemInRow(dType)
			else: # create new dataRatioItem
				dataRatioItem = DataRatioItem(dType)
				dataRatioItem.setSelector("", exact, "")
			dataRatioItem.setAttribute(dfType, value) # add value
			dmRow.setDataRatioItem(dataRatioItem)

		if dType == "reviewer":
			if dmRow.getDataReviewer(): # DataReviewer exists
				dataReviewer = dmRow.getDataReviewer()
			else:
				dataReviewer = DataReviewer()
			dataReviewer.setAttribute(dfType, value)
			dmRow.setDataReviewer(dataReviewer)

		if dType == "dipsquestion": # DataDips exists
			if dmRow.getDataDips(): 
				dips = dmRow.getDataDips()
			else:
				dips = DataDips()
			dips.setQuestion(dfType, value)
			dmRow.setDataDips(dips)

		if not dmRow.getEvRelationship(): # add evidence relationship to dmRow
			if evRelationship is True:				
				dmRow.setEvRelationship("supports")
			elif evRelationship is False:
				dmRow.setEvRelationship("refutes")

		evqs = row[14]
		evqsVal = row[15]
		if evqs and evqsVal:
			if evqs == "groupRandom" and not dmRow.getGroupRandom():
				dmRow.setGroupRandom(evqsVal)
			elif evqs == "parallelgroup" and not dmRow.getParallelGroup():
				dmRow.setParallelGroup(evqsVal)

	return annotation

######################### QUERY MP Material ##########################
# query material items for claim annotation
# return list of MaterialItems
def queryMpMaterial(conn, annotation, claimid):

	qry = """	
	select mann.type, mf.material_field_type, mf.value_as_string, mf.value_as_number, s.exact, s.prefix, s.suffix, mann.mp_data_index, mann.ev_supports
	from mp_material_annotation mann join oa_material_body mbody on mann.has_body = mbody.id
	join material_field mf on mf.material_body_id = mbody.id
	left join oa_target t on mann.has_target = t.id
	left join oa_selector s on t.has_selector = s.id
	where mann.mp_claim_id = %s
	""" % (claimid)

	results = []

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():

		mType = row[0]  # material type
		mfType = row[1] # material field 

		exact = row[4]; value = str(row[2] or row[3]) # value as string or number
		index = row[7] # data & material index
		evRelationship = row[8] # EV supports or refutes

		if annotation.getSpecificDataMaterial(index) == None:
			dmRow = DataMaterialRow() # create new row of data & material

			if evRelationship:				
				dmRow.setEvRelationship("supports")
			else:
				dmRow.setEvRelationship("refutes")

			if mType in ["object_dose","subject_dose"]: # dose
				doseItem = MaterialDoseItem(mType)
				doseItem.setAttribute(mfType, value)
				doseItem.setSelector("", exact, "")
				dmRow.setMaterialDoseItem(doseItem)

			elif mType == "participants":
				partItem = MaterialParticipants(value)
				partItem.setSelector("", exact, "")
				dmRow.setParticipants(partItem)

			elif mType == "phenotype":
				phenoItem = MaterialPhenotypeItem()
				phenoItem.setAttribute(mfType, value)
				dmRow.setPhenotype(phenoItem)

			annotation.setSpecificDataMaterial(dmRow, index)

		else: # current row of material & material exists 
			dmRow = annotation.getSpecificDataMaterial(index)

			if dmRow.getEvRelationship() == None and evRelationship is True:
				dmRow.setEvRelationship("supports")
			elif dmRow.getEvRelationship() == None and evRelationship is False:
				dmRow.setEvRelationship("refutes")

			if mType in ["object_dose","subject_dose"]:
				if dmRow.getMaterialDoseInRow(mType): # current MaterialItem exists
					doseItem = dmRow.getMaterialDoseInRow(mType)
				else:
					doseItem = MaterialDoseItem(mType) 

				doseItem.setAttribute(mfType, value)
				doseItem.setSelector("", exact, "")				
				dmRow.setMaterialDoseItem(doseItem)

			elif mType == "participants":
				if dmRow.getParticipantsInRow(): # participants exists
					partItem = dmRow.getParticipantsInRow()
					partItem.setValue(value)
				else:
					partItem = MaterialParticipants(value)
					dmRow.setParticipants(partItem)
				partItem.setSelector("", exact, "")

			elif mType == "phenotype":
				if dmRow.getPhenotype():
					phenoItem = dmRow.getPhenotype()
				else:			
					phenoItem = MaterialPhenotypeItem()
				phenoItem.setAttribute(mfType, value)
				dmRow.setPhenotype(phenoItem)

	return annotation


######################### QUERY Highlight Annotaiton ##########################
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
