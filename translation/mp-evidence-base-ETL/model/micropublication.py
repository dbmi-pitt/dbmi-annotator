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
class DMItem:

	def __init__(self, prefix, exact, suffix, dmIdx):
		self.prefix = prefix
		self.exact = exact
		self.suffix = suffix
		self.dmIdx = dmIdx

	def setSelector(self, prefix, exact, suffix):
		self.prefix = prefix
		self.exact = exact
		self.suffix = suffix		
		
	def getDmIdx(self):
		return self.dmIdx

	def setDmIdx(idx):
		self.dmIdx = idx

# # Method that supports data & material
# class Method():
# 	def __init__(self, entered_value, inferred_value):
# 		self.entered_value = entered_value
# 		self.inferred_value = inferred_value

# Data item in row of data 
class DataRatioItem(DMItem):

	def __init__(self, field):
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

	def addValue(self, value):
		self.value = value
	def addType(self, type):
		self.type = type
	def addDirection(self, direction):
		self.direction = direction

# Questions for dips score
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

# Reviewer
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
	
# Material dose
class MaterialDoseItem(DMItem):
	def __init__(self, field):
		self.field = field # options: objectdose or subjectdose
		self.value = None 
		self.duration = None
		self.formulation = None
		self.regimens = None

	def setAttribute(self, name, value):
		if name == "value":
			self.value = value
		elif name == "duration":
			self.duration = value
		elif name == "formulation":
			self.formulation = value 
		elif name == "regimens":
			self.regimens = value 

# Material participants
class MaterialParticipants(DMItem):
	def __init__(self, value):
		self.value = value

	def setValue(self, value):
		self.value = value

# Material phenotype
class MaterialPhenotypeItem():
	def __init__(self):
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

# represents single row of data & material in annotation table
class DataMaterialRow(object):

	def __init__(self):
		self.index = 1 # mp data index for claim, default 0 
		self.dataMaterialRowD = {"auc": None, "cmax": None, "clearance": None, "halflife": None, "dipsquestion": None, "reviewer": None, "participants": None, "object_dose": None, "subject_dose": None, "evRelationship": None, "phenotype": None, "grouprandom": None, "parallelgroup": None}

	# questions for method: group randomization and parellel group design
	def setGroupRandom(self, value): 
		self.dataMaterialRowD["grouprandom"] = value
	def getGroupRandom(self):
		return self.dataMaterialRowD["grouprandom"]

	def setParallelGroup(self, value): 
		self.dataMaterialRowD["parallelgroup"] = value
	def getParallelGroup(self):
		return self.dataMaterialRowD["parallelgroup"]

	# phenotype get and set
	def setPhenotype(self, obj): 
		self.dataMaterialRowD["phenotype"] = obj
	def getPhenotype(self):
		return self.dataMaterialRowD["phenotype"]

	# evidence relationship (supports/refutes) get and set
	def setEvRelationship(self, value): 
		self.dataMaterialRowD["evRelationship"] = value
	def getEvRelationship(self):
		return self.dataMaterialRowD["evRelationship"]

	# Mp data item get and set
	def setDataRatioItem(self, obj): # obj: DataRatioItem
		if self.dataMaterialRowD[obj.field] != None:
			#print "[Warning] Data item already has the field: " + obj.field
			return
		elif obj.field in ["auc", "cmax", "clearance", "halflife"]:
			self.dataMaterialRowD[obj.field] = obj
		else:
			print "[Error] data item undefined: " + obj.field

	# Mp data ratio
	def getDataRatioItemInRow(self, field): # return DataRatioItem
		if field in ["auc", "cmax", "clearance", "halflife"]:
			return self.dataMaterialRowD[field]
		else:
			print "[Error] get DataRatioItem field error: " + field

	# Mp data dips questions
	def setDataDips(self, obj):
		self.dataMaterialRowD["dipsquestion"] = obj
	def getDataDips(self):
		return self.dataMaterialRowD["dipsquestion"]

	# Mp data reviewer information
	def setDataReviewer(self, obj):
		self.dataMaterialRowD["reviewer"] = obj
	def getDataReviewer(self):
		return self.dataMaterialRowD["reviewer"]


	# Mp material Dose get and set
	def setMaterialDoseItem(self, obj): # obj: MaterialDoseItem
		if self.dataMaterialRowD[obj.field] != None:
			#print "[Warning] Data item already has the field: " + obj.field
			return
		elif obj.field in ["subject_dose", "object_dose"]:
			self.dataMaterialRowD[obj.field] = obj
		else:
			print "[Error] material item undefined: " + obj.field

	def getMaterialDoseInRow(self, field): # return MaterialDoseItem
		if field in ["subject_dose","object_dose"]:
			return self.dataMaterialRowD[field]
		else:
			print "[Error] get MaterialItem field error: " + field

	# Mp material participants get and set
	def setParticipants(self, obj): # obj: MatarialParticipants
		if self.dataMaterialRowD["participants"] != None:
			#print "[Warning] Data item already has the field: participants"
			return
		else:
			self.dataMaterialRowD["participants"] = obj

	def getParticipantsInRow(self): # return MatarialParticipants
		return self.dataMaterialRowD["participants"]	

	# get dict of all data & material items
	def getDataMaterialRow(self): # return one row of data & material items
		return self.dataMaterialRowD

	# data & material index get and set
	def getDmIndex(self):
		return self.index
		
	def setDmIndex(self, index):
		self.index = index

# Define data structure for mp annotation
class Annotation(object):

	def __init__(self):
		self.claimid = None; self.urn = None
		self.csubject = None; self.cpredicate = None; self.cobject = None
		self.label = None; self.source = None
		self.prefix = None; self.exact = None; self.suffix = None # oa selector

		self.method = None  # user entered method
		self.negation = None # assertion negation supports or refutes
		self.rejected = None # 'reason': '<rejected reason>|<comments>'

		self.csubject_enantiomer = False
		self.csubject_metabolite = False
		self.cobject_enantiomer = False
		self.cobject_metabolite = False

		self.mpDataMaterialD = {} # data and material dict	

	def setOaSelector(self, prefix, exact, suffix):
		self.prefix = prefix
		self.exact = exact
		self.suffix = suffix

	# get all data and material rows
	def getDataMaterials(self): # return list of DataMaterialRows
		return self.mpDataMaterialD

	# single data and material get and set
	def getSpecificDataMaterial(self, idx): # return DataMaterialRow
		if idx in self.mpDataMaterialD:
			return self.mpDataMaterialD[idx]
		else:
			return None

	def setSpecificDataMaterial(self, dmRow, index): # input DataMaterialRow
		if index in self.mpDataMaterialD:
			print "[Warning] Data row already been filled - index: " + str(index)
		else:
			self.mpDataMaterialD[index] = dmRow

	def setSubjectPC(enantiomer, metabolite):
		self.csubject_enantiomer = enantiomer
		self.csubject_metabolite = metabolite

	def setObjectPC(enantiomer, metabolite):
		self.cobject_enantiomer = enantiomer
		self.cobject_metabolite = metabolite
