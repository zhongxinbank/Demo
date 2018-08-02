# -*- coding: utf-8 -*-
from peewee import *
from database.orm.action_log_orm import ActionLog
import uuid, json, os
import traceback
from os import walk

def empty_database():
	try:
		ActionLog.delete()
	except BaseException as e:
		print('Unknow error When Delete Database - reason "%s"' % str(e))
		print(traceback.format_exc())
		exit()

#TODO: Change the function for only seeding model data and leave all the other data for me
def seed_data():
    try:
        ActionLog.create(
            _id = str(uuid.uuid4()),
            action_name = "植入Seed数据",
            action_type = "development",
            action_status = "成功",
            action_msg = "植入Seed数据",
            user_id = "admin"
        )
    except BaseException as e:
        print('Unknow error When Create Seed Records - reason "%s"' % str(e))
        print(traceback.format_exc())
        exit()

if __name__ == '__main__':

	MYSQL_PORT=None
	MYSQL_USER=None
	MYSQL_PSWD=None
	MYSQL_HOST=None
	db=None

	try:
		MYSQL_PORT = int(os.environ['MYSQL_PORT'])
		MYSQL_USER = os.environ["MYSQL_USER"]
		MYSQL_HOST = os.environ["MYSQL_HOST"]
		MYSQL_PSWD = os.environ["MYSQL_PSWD"]
	except KeyError as e:
		print ('MYSQL Environment Variable Keyerror - reason "%s"' % str(e))
		MYSQL_PORT = 3306
		MYSQL_USER = 'root'
		MYSQL_PSWD = 'root2018'
		MYSQL_HOST = 'localhost'
	except BaseException as e:
		print('Unknow error - reason "%s"' % str(e))
		exit()

	mysql_db =MySQLDatabase(
		'ellison', 
		user=MYSQL_USER, 
		password=MYSQL_PSWD, 
		host=MYSQL_HOST, 
		port=MYSQL_PORT, 
		charset='utf8mb4'
	)
	mysql_db.create_tables([ActionLog])
	mysql_db.connect()
	empty_database()
	seed_data()
	print("Finished seeding data")



