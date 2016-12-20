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

import psycopg2
import uuid
import datetime
from sets import Set
import sys  

# pip install bcrypt
import bcrypt

reload(sys)  
sys.setdefaultencoding('utf8')

if len(sys.argv) > 4:
	PG_HOST = str(sys.argv[1])
	PG_USER = str(sys.argv[2])
	PG_PWD = str(sys.argv[3])
	EMAIL = str(sys.argv[4])
	PASSWORD = str(sys.argv[5])
else:
	print "Usage: create-new-user.py <pg hostname> <pg username> <pg password> <user email> <password>"
	sys.exit(1)

def connect_postgreSQL():

	myConnection = psycopg2.connect(host=PG_HOST, user=PG_USER, password=PG_PWD, dbname='dbmiannotator')	
	print("Postgres connection created")	
	return myConnection


def createNewUser(conn):
	if not EMAIL or not PASSWORD:
		print "[ERROR] EMAIL or PASSWORD not provided!"
		return 

	cur = conn.cursor()
	userid = None

	# check if email is taken
	qry0 = "SELECT * FROM \"user\" WHERE email = '%s';" % (EMAIL)
	print qry0
	cur.execute(qry0)
	for row in cur.fetchall():
		userid = row[0]
	if userid:
		print "[INFO] email is already taken!"
		return

	curr_date = datetime.datetime.now()
	hash_password = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt())
	hash_password = "$2a" + hash_password[3:]

	# create new user
	qry1 = "INSERT INTO \"user\"(uid, username, admin, manager, email, status, last_login_date, registered_date, activation_id, password) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (uuid.uuid4().hex, EMAIL, 0, 0, EMAIL, 0, curr_date, curr_date, 0, hash_password)
	cur.execute(qry1)

	cur.execute(qry0)
	for row in cur.fetchall():
		userid = row[0]
	
	if userid: # add user profile		
		qry2 = "INSERT INTO user_profile(uid, set_id, status, created) values('%s', (SELECT id FROM plugin_set WHERE type = '%s'), %s, '%s')" % (userid, 'MP', True, curr_date)
		cur.execute(qry2)
	conn.commit()


def main():

	print("[INFO] connect postgreSQL ...")
	conn = connect_postgreSQL()
	createNewUser(conn)
	conn.close()

	print("[INFO] create new user completed!")


if __name__ == '__main__':
	main()
