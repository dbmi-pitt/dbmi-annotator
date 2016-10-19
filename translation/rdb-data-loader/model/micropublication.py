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

# Data item in row of data 
class DataItem(DMItem):

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
	

# Material dose item in material
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

# Material participant item in material
class MaterialParticipants(DMItem):
	def __init__(self, value):
		self.value = value

	def setValue(self, value):
		self.value = value


# represents single row of data & material in annotation table
class DataMaterialRow(object):

	def __init__(self):
		self.index = 1 # mp data index for claim, default 0 
		self.dataMaterialRowD = {"auc": None, "cmax": None, "clearance": None, "halflife": None, "participants": None, "object_dose": None, "subject_dose": None, "evRelationship": None}

	def setEvRelationship(self, value): # evidence relationship supports/refutes
		self.dataMaterialRowD["evRelationship"] = value

	def getEvRelationship(self):
		return self.dataMaterialRowD["evRelationship"]

	def setDataItem(self, obj): # obj: DataItem
		if self.dataMaterialRowD[obj.field] != None:
			#print "[Warning] Data item already has the field: " + obj.field
			return
		elif obj.field in ["auc", "cmax", "clearance", "halflife"]:
			self.dataMaterialRowD[obj.field] = obj
		else:
			print "[Error] data item undefined: " + obj.field

	def setMaterialDoseItem(self, obj): # obj: MaterialDoseItem
		if self.dataMaterialRowD[obj.field] != None:
			#print "[Warning] Data item already has the field: " + obj.field
			return
		elif obj.field in ["subject_dose", "object_dose"]:
			self.dataMaterialRowD[obj.field] = obj
		else:
			print "[Error] material item undefined: " + obj.field

	def setParticipants(self, obj): # obj: MatarialParticipants
		if self.dataMaterialRowD["participants"] != None:
			#print "[Warning] Data item already has the field: participants"
			return
		else:
			self.dataMaterialRowD["participants"] = obj
	
	def getDataMaterialRow(self): # return one row of data & material items
		return self.dataMaterialRowD

	def getDataItemInRow(self, field): # return DataItem
		if field in ["auc", "cmax", "clearance", "halflife"]:
			return self.dataMaterialRowD[field]
		else:
			print "[Error] get DataItem field error: " + field

	def getMaterialDoseInRow(self, field): # return MaterialDoseItem
		if field in ["subject_dose","object_dose"]:
			return self.dataMaterialRowD[field]
		else:
			print "[Error] get MaterialItem field error: " + field

	def getParticipantsInRow(self): # return MatarialParticipants
		return self.dataMaterialRowD["participants"]

	def getDmIndex(self):
		return self.index
		
	def setDmIndex(self, index):
		self.index = index

# Define data structure for mp annotation
class Annotation(object):

	def __init__(self):
		self.csubject = None; self.cpredicate = None; self.cobject = None
		self.label = None
		self.source = None
		self.prefix = None; self.exact = None; self.suffix = None # oa selector
		self.mpDataMaterialD = {} # data and material dict		

	def setOaSelector(self, prefix, exact, suffix):
		self.prefix = prefix
		self.exact = exact
		self.suffix = suffix

	def getDataMaterials(self): # return list of DataMaterialRows
		return self.mpDataMaterialD

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
