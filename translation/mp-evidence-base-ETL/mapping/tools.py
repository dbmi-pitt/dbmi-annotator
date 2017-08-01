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

import os.path, sys, csv
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from model.Concept import *
from postgres import connection as pgconn
from postgres import omopConceptQry as pgcp

vocabIdConvertDict = {44819104 : "RxNorm", 44819103 : "NDFRT", 44819136 : "MESH"}

## return concepts in dict {"concept name": Concept}
def getDrugMappingDict(inputfile, pgconn):
	drugMapD = {}
	reader = csv.DictReader(utf_8_encoder(open(inputfile, 'r')))
	next(reader, None) # skip the header
        
	for row in reader:	
		name = row["name"] # this is annotated drug name (not standardized concept name)
		if name and name not in drugMapD:
			concept_code = None; vocab_id = None; concept_id = None
			if row["RxNorm"].strip() != "":
				concept_code = row["RxNorm"].strip()
				vocab_id = 44819104 # RxNorm omop concept id
                                
                        elif row["NDFRT"].strip() != "":
                                concept_code = row["NDFRT"].strip()
                                vocab_id = 44819103 # NDFRT concept id
                                
			elif row["MESH"].strip() != "":	   
				concept_code = row["MESH"].strip()
				vocab_id = 44819136 # MeSH concept id                                

			if row["conceptId"].strip() != "":
				concept_id = row["conceptId"].strip()                                
                        else:
                                if concept_code and vocab_id:
                                        concept_id = pgcp.getConceptIdByConceptCode(pgconn, concept_code, vocabIdConvertDict[vocab_id])
                        # print "tools.py, code (%s), vid(%s), cid(%s)" % (concept_code, vocab_id, concept_id)
			if concept_code and vocab_id and concept_id:
				drugMapD[name] = Concept(name, concept_code, vocab_id, concept_id)
	return drugMapD


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def printMapping(inputfile):
	print inputfile
	testD = getDrugMappingDict(inputfile)
	for k, v in testD.iteritems():
		print k
		print v.name, v.concept_code, v.vocabulary_id, v.concept_id

if __name__ == '__main__':
	DRUG_MAPPING = "./drug-list-mapped.csv"
	printMapping(DRUG_MAPPING)
