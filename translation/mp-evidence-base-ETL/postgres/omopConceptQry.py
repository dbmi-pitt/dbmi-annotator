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

# query concept id and concept code for specific vocabulary 
def getConceptCodeByVocabId(conn, vocabId):
	
	cur = conn.cursor()
	qry = """
	select concept_id, concept_code, concept_name from public.concept where vocabulary_id = %s
	""" % vocabId
	cur.execute(qry)
	return cur.fetchall()


# query concept id by concept code and vocabulary id
def getConceptIdByConceptCode(conn, conceptCode, vocabId):
        
	cur = conn.cursor()
	qry = """
        select * from public.concept where concept_code = '%s' and vocabulary_id = '%s';
	""" % (conceptCode, vocabId)
        
	cur.execute(qry)
        for row in cur.fetchall():
	        return row[0]
