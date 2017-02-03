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

import csv
import uuid
import datetime
from sets import Set
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

## validate query results and the results from csv
## rttype: boolean
def validateResults(conn, csvD):
	rdbD = queryDocAndDataCnt(conn)
	return compareTwoDicts(csvD, rdbD)

## query MP claim, rtype: dict with document url and counts of annotation
def queryDocAndDataCnt(conn):
	claimDict = {}

	qry = """
set schema 'ohdsi';
select distinct t.has_source, cann.urn, max(dann.mp_data_index)
from mp_claim_annotation cann join oa_claim_body cbody on cann.has_body = cbody.id
join oa_target t on cann.has_target = t.id
left join mp_data_annotation dann on cann.id = dann.mp_claim_id
group by t.has_source, cann.urn
order by t.has_source, cann.urn """

	cur = conn.cursor()
	cur.execute(qry)

	for row in cur.fetchall():
		document = row[0]; claim_urn = row[1]; cnt = row[2]

		if not cnt or cnt == "":
			cnt = 1

		if document in claimDict:				
			claimDict[document] += cnt
		else:
			claimDict[document] = cnt

	return claimDict

## compare two dicts
## rtype: boolean (same: True, different: False)
def compareTwoDicts(dict1, dict2):
	if len(dict1) != len(dict2):
		return False

	for k,v in dict1.iteritems():
		if k in dict2 and dict2[k] == v:
			print "[INFO] document (%s) have MP data (%s) validated" % (k, v)
		else:
			print "[ERROR] document (%s) have MP data (%s) from dict1 but data (%s) from dict 2" % (k, v, dict2[k])
			return False
	return True

