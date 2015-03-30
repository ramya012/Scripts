#!/usr/bin/python
__author__ ='ramya'
__version__ ='1.0'

"""
This class handles, Creating the subnets and maintain the log file 
"""
import argparse
import json
import boto
import boto.ec2
import time
import sys
import logging
import os

"""
Creating the log file and load the configuration file
"""
lgr = logging.getLogger('MyLogger')
lgr.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('Citrix_Env.log')
lgr.addHandler(file_handler)

state = ['start','stop']
parser = argparse.ArgumentParser()
parser.add_argument('-s', help="Specify whether to start or stop the instance" )
args = parser.parse_args()
status = args.s.lower()
if status not in state:
	lgr.info("Provide the -s with start or stop")
	sys.exit(0)
conn = boto.ec2.connect_to_region('us-east-1')
all_instances_from_API = []
all_instances = conn.get_only_instances()

for instance in all_instances:
	all_instances_from_API.append(instance.id)	

def env_start_stop(path=None):
	global lgr,conn,all_instances_from_API,status
	#checking the path is empty or not
	if not path:
		lgr.info("Path for json file is empty")
		sys.exit(0)
	
	#checking whether file exists or not
	if not os.path.isfile(path):
		lgr.error("unable to find required json file "+str(path))
		sys.exit(0)

	with open(path,"r") as fp:
		input = json.load(fp)
	instances_from_Json = input['ids']
	#print all_instances_from_API
	for instance_id in instances_from_Json:
		if instance_id in all_instances_from_API:
			lgr.info(instance_id + " exists")
			if status == "stop":
				instances = conn.stop_instances(instance_ids = instance_id)
				lgr.info(instance_id + "is stopped")
			else:
				instances = conn.start_instances(instance_ids = instance_id)
				lgr.info(instance_id + "is started")
		else:
			lgr.info(instance_id + " does not exists")
			print instance_id + " does not exists"
			sys.exit(0)
		
	
env_start_stop("Citrix_Instances.json")


		

