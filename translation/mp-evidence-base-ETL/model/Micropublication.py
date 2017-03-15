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

# Parent class of data or material item

## Qualifier
class Qualifier:

	def __init__(self, qvalue, subject, predicate, object):	
		self.qvalue = qvalue
		self.subject = subject
		self.predicate = predicate
		self.object = object
		self.concept_code = None
		self.vocabulary_id = None
		self.qualifier_type_concept_code = None
		self.qualifier_type_vocabulary_id = None
		self.qualifier_role_concept_code = None
		self.qualifier_role_vocabulary_id = None
		self.enantiomer = None
		self.metabolite = None

	def setTypeDrugProduct(self):
		self.qualifier_type_concept_code = "DIDEO_00000005"
		self.qualifier_type_vocabulary_id = -9900002

	def isDrugProduct(self):
		if self.qualifier_type_concept_code == "DIDEO_00000005":
			return True
		return False

	def setTypeEnzyme(self):
		self.qualifier_type_concept_code = "OBI_0000427"
		self.qualifier_type_vocabulary_id = -9900003

	def isEnzyme(self):
		if self.qualifier_type_concept_code == "OBI_0000427":
			return True
		return False

	def setRolePrecipitant(self):
		self.qualifier_role_concept_code = "DIDEO_00000013"
		self.qualifier_role_vocabulary_id = -9900004

	def isRolePrecipitant(self):
		if self.qualifier_role_concept_code == "DIDEO_00000013":
			return True
		return False

	def setRoleObject(self):
		self.qualifier_role_concept_code = "DIDEO_00000012"
		self.qualifier_role_vocabulary_id = -9900005

	def isRoleObject(self):
		if self.qualifier_role_concept_code == "DIDEO_00000012":
			return True
		return False

	def setRoleProbeSubstrate(self):
		self.qualifier_role_concept_code = "probe1"
		self.qualifier_role_vocabulary_id = "probe2"

	def isRoleProbeSubstrate(self):
		if self.qualifier_role_concept_code == "probe1":
			return True
		return False

## MP Annotation ##############################################################
class Annotation(object):

	def __init__(self, urn, source, label, method, creator, date):
		self.source = source
		self.urn = urn
		self.creator = creator
		self.method = method	
		self.date_created = date
		self.label = label
		self.csubject = None
		self.cpredicate = None
		self.cobject = None
		self.cqualifier = None
		self.claimid = None
		self.prefix = None; self.exact = None; self.suffix = None # oa selector
		self.date_created = None
		self.rejected_statement = None
		self.rejected_statement_reason = None
		self.rejected_statement_comment = None
	
	def setOaSelector(self, prefix, exact, suffix):
		self.prefix = prefix
		self.exact = exact
		self.suffix = suffix

	def getPrecipitantQualifier(self):
		if self.csubject and self.csubject.isRolePrecipitant():
			return self.csubject
		elif self.cobject and self.cobject.isRolePrecipitant():
			return self.cobject
		elif cqualifier and self.cqualifier.isRolePrecipitant():
			return self.cqualifier
		else:
			return None

	def getObjectQualifier(self):
		if self.csubject and self.csubject.isRoleObject():
			return self.csubject
		elif self.cobject and self.cobject.isRoleObject():
			return self.cobject
		elif self.cqualifier and self.cqualifier.isRoleObject():
			return self.cqualifier
		else:
			return None

	def getEnzyme(self):
		if self.cobject and self.cobject.isEnzyme():
			return self.cobject
		elif self.cqualifier and self.cqualifier.isEnzyme():
			return self.cqualifier

	def setRejected(self, rej_statement, rej_reason, rej_comment):
		self.rejected_statement = rej_statement
		self.rejected_statement_reason = rej_reason
		self.rejected_statement_comment = rej_comment


## MP Statement annotation
class Statement(Annotation):
	def __init__(self, csubject, cpredicate, cobject):
		Annotation.__init__(self, urn, source, label, method, creator, date)
		self.negation = None # assertion negation supports or refutes


## DDI clinical trial annotation
class ClinicalTrial(Annotation):

	def __init__(self, urn, source, label, method, creator, date):
		Annotation.__init__(self, urn, source, label, method, creator, date)
		self.mpDataMaterialD = {} # data & material dict {dmIdx: ClinicalTrialDMRow}

	def setQualifiers(self, csubject, cpredicate, cobject, cqualifier):
		self.csubject = csubject
		self.cpredicate = cpredicate
		self.cobject = cobject	
		self.cqualifier = cqualifier		

	def getDataMaterials(self): # return list of DataMaterials
		return self.mpDataMaterialD

	def setDataMaterials(self, mpDataMaterialD): # add DataMaterials
		self.mpDataMaterialD = mpDataMaterialD

	def getSpecificDataMaterial(self, idx): # return ClinicalTrialDMRow
		if idx in self.mpDataMaterialD:
			return self.mpDataMaterialD[idx]
		else:
			return None

	def setSpecificDataMaterial(self, dmRow, dmIdx): # add DataMaterialRow
		if isinstance(dmRow, ClinicalTrialDMRow):
			self.mpDataMaterialD[dmIdx] = dmRow
		else:
			print "[ERROR] ClinicalTrial - setSpecificDataMaterial dmRow undefined"


## Phenotype clinical study annotation
class PhenotypeClinicalStudy(Annotation):

	def __init__(self, urn, source, label, method, creator, date):
		Annotation.__init__(self, urn, source, label, method, creator, date)
		self.mpDataMaterialD = {} # data and material dict {dmIdx: PhenotypeDMRow}	

	def getDataMaterials(self): # return list of DataMaterials
		return self.mpDataMaterialD

	def setDataMaterials(self, mpDataMaterialD): # add DataMaterials
		self.mpDataMaterialD = mpDataMaterialD

	def getSpecificDataMaterial(self, idx): # return DataMaterialRow
		if idx in self.mpDataMaterialD:
			return self.mpDataMaterialD[idx]
		else:
			return None

	def setSpecificDataMaterial(self, dmRow, index): # add PhenotypeDMRow
		if index in self.mpDataMaterialD:
			print "[Warning] Data row already been filled - index: " + str(index)
		else:
			self.mpDataMaterialD[index] = dmRow

## Case Report annotation
class CaseReport(Annotation):
 
	def __init__(self, urn, source, label, method, creator, date):
		Annotation.__init__(self, urn, source, label, method, creator, date)
		self.mpDataMaterialD = {} # data and material dict {dmIdx: CaseReportDMRow}	

	# get all data and material rows
	def getDataMaterials(self): # return list of DataMaterials
		return self.mpDataMaterialD

	def setDataMaterials(self, mpDataMaterialD): # add DataMaterials
		self.mpDataMaterialD = mpDataMaterialD

	# single data and material get and set
	def getSpecificDataMaterial(self, idx): # return CaseReportDMRow
		if idx in self.mpDataMaterialD:
			return self.mpDataMaterialD[idx]
		else:
			return None

	def setSpecificDataMaterial(self, dmRow, index): # add CaseReportDMRow
		if index in self.mpDataMaterialD:
			print "[Warning] Data row already been filled - index: " + str(index)
		else:
			self.mpDataMaterialD[index] = dmRow

## Data and Material as individual evidence (row of data & material in annotation table) ##############################################################################
class DMRow(object):
	def __init__(self, dmIdx):
		self.dmIdx = dmIdx
		self.ev_supports = None # True or False

class ClinicalTrialDMRow(DMRow):
	def __init__(self, dmIdx):
		DMRow.__init__(self, dmIdx)
		self.participants = None
		self.precipitant_dose = None
		self.object_dose = None
		self.auc = None
		self.cmax = None
		self.clearance = None
		self.halflife = None
		self.parallelgroup = None
		self.grouprandom = None

class PhenotypeDMRow(DMRow):
	def __init__(self, dmIdx):
		DMRow.__init__(self, dmIdx)
		self.participants = None
		self.probesubstrate_dose = None
		self.phenotype = None
		self.auc = None
		self.cmax = None
		self.clearance = None
		self.halflife = None
		self.parallelgroup = None
		self.grouprandom = None

class CaseReportDMRow(DMRow):
	def __init__(self, dmIdx):
		DMRow.__init__(self, dmIdx)
		self.revewer = None
		self.precipitant_dose = None
		self.object_dose = None
		self.dipsquestion = None

## Specific data or material item as component of evidence #######################
class DMItem(object):
	def __init__(self):
		self.prefix = None
		self.exact = None
		self.suffix = None

	def setSelector(self, prefix, exact, suffix):
		self.prefix = prefix
		self.exact = exact
		self.suffix = suffix				


# DDI Clinical trial, Phenotype clinial study: participants
class MaterialParticipants(DMItem):
	def __init__(self, value):
		self.value = value

	def setValue(self, value):
		self.value = value

## DDI Clinical trial, Case Report: Material dose
class MaterialDoseItem(DMItem):
	def __init__(self, field):
		DMItem.__init__(self)
		self.field = field # precipitant_dose, object_dose, probesubstrate_dose
		self.drugname = None
		self.value = None 
		self.duration = None
		self.formulation = None
		self.regimens = None

	def setAttributes(self, drugname, value, formulation, duration, regimens):
		self.drugname = drugname
		self.value = value
		self.duration = duration
		self.formulation = formulation
		self.regimens = regimens	

	def setAttribute(self, name, value):
		if name == "drugname":
			self.drugname = value
		elif name == "value":
			self.value = value
		elif name == "duration":
			self.duration = value
		elif name == "formulation":
			self.formulation = value 
		elif name == "regimens":
			self.regimens = value 
		else:
			print "[ERROR] MaterialDoseItem: undefined attribute name!"


# DDI Clinical trial, Phenotype clinial study: auc/cmax/clearance/halflife ratio
class DataRatioItem(DMItem):

	def __init__(self, field):
		DMItem.__init__(self)
		self.field = field
		self.value = None
		self.type = None
		self.direction = None

	def setAttribute(self, name, value):
		if name == "value":
			self.value = value
		elif name == "type":
			self.type = value
		elif name == "direction":
			self.direction = value 

	def setAttributes(self, value, type, direction):
		self.value = value
		self.type = type
		self.direction = direction

	# def addValue(self, value):
	# 	self.value = value
	# def addType(self, type):
	# 	self.type = type
	# def addDirection(self, direction):
	# 	self.direction = direction

## Phenotype clinical study:  Material phenotype
class MaterialPhenotypeItem():
	def __init__(self):
		DMItem.__init__(self)
		self.ptype = None
		self.value = None 
		self.metabolizer = None
		self.population = None

	def setAttribute(self, name, value):
		if name == "type":
			self.ptype = value
		elif name == "value":
			self.value = value
		elif name == "metabolizer":
			self.metabolizer = value 
		elif name == "population":
			self.population = value 

## Case Report: Questions for dips score
class DataDips():
	def __init__(self):
		self.dipsQsDict = {}

	def getDipsDict(self):
		return self.dipsQsDict

	def setDipsDict(self, dipsQsDict):
		self.dipsQsDict = dipsQsDict

	def setQuestion(self, qs, value):
		self.dipsQsDict[qs] = value

	def getAnswerByQs(self, qs):
		return self.dipsQsDict[qs]

## Case Report: Reviewer
class DataReviewer():
	def __init__(self):
		self.reviewer = None	
		self.date = None
		self.total = None
		self.lackinfo = None

	def setAttribute(self, name, value):
		if name == "reviewer":
			self.reviewer = value
		elif name == "date":
			self.date = value
		elif name == "total":
			self.total = value 
		elif name == "lackinfo":
			self.lackinfo = value 
	

# # Method that supports data & material
# class Method():
# 	def __init__(self, entered_value, inferred_value):
# 		self.entered_value = entered_value
# 		self.inferred_value = inferred_value

def createSubAnnotation(urn, source, label, method, email, date):
	if method == "DDI clinical trial":
		return ClinicalTrial(urn, source, label, method, email, date)
	elif method == "Phenotype clinical study":
		return PhenotypeClinicalStudy(urn, source, label, method, email, date)
	elif method == "Case Report":
		return PhenotypeClinicalStudy(urn, source, label, method, email, date)
	elif method == "Statement":
		return Statement(urn, source, label, method, email, date)
	return None
