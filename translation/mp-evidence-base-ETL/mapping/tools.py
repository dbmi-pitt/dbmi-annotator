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
from model.Micropublication import *

DRUG_MAPPING = "./drug-list-mapped.csv"

## return concepts in dict {"concept name": Concept}
def getDrugMappingDict(csvfile):
	drugMapD = {}
	reader = csv.DictReader(utf_8_encoder(open(csvfile, 'r')))
	next(reader, None) # skip the header
	for row in reader:	
		if row["name"] and row["name"] not in drugMapD:
			concept_code = None; vocab_id = None; concept_id = None
			if row["RxNorm"] and row["RxNorm"] != "null":
				concept_code = row["RxNorm"]
				vocab_id = "RxNorm"
			elif row["metabolite"] and row["metabolite"] != "null":				
				concept_code = row["metabolite"]
				vocab_id = "MeSH"

			concept = Concept()
