#!/usr/bin/pyhton
"""
python version:2.7.6
Description:To stop and start the instance through command prompt
To run the program:python <name of the file>.py -i <instance id> -s <start/stop>
help:python <name of the file>.py -h
"""
import argparse
import boto.ec2
import logging
import os
import time
import sys

"""
Creating a logger,file handler and connection
"""
lgr = logging.getLogger('MyLogger')
lgr.setLevel(logging.DEBUG)
fh = logging.FileHandler('instanceLogger.log')
lgr.addHandler(fh)
conn = boto.ec2.connect_to_region('us-east-1')
all_Instances = []
reservations = conn.get_all_reservations()
	
def instance_start(instanceId):
	"""
	Start a particular Instance under particular region
	"""
	global conn,lgr

	if not instanceId:
		lgr.info("InstanceId is empty")
	try:
		instances = conn.start_instances(instance_ids = instanceId)
		for instance in instances:
			while instance.state != 'running':
				lgr.info("Waiting for " + str(instance.id) +" to run: ")
				time.sleep(4)
				instance.update()
		lgr.info(str(instance.id)+ " started ")	
	except Exception, message:
		lgr.error(str(message))
		sys.exit(0)
	
def instance_stop(instanceId):
	"""
	Stop a particular Instance under particular region
	"""
	if not instanceId:
		lgr.info("InstanceId is empty")
	try:
		instances = conn.stop_instances(instance_ids = instanceId)
		for instance in instances:
			while instance.state != 'stopped':
				lgr.info("Waiting for "+str(instance.id) +" to stopping " )
				time.sleep(4)
				instance.update()
		lgr.info(str(instance.id)+" stopped ")	
	except Exception, message:
		lgr.error(str(message))
		sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument('-i',help="pass a instance name")
parser.add_argument('-s', help="Specify whether to start or stop the instance" )
args = parser.parse_args()

for res in reservations:
	for inst in res.instances:
		all_Instances.append(str(inst.id))
		if not args.i and not args.s:
			if 'Name' in inst.tags:
				print "%s (%s) [%s]" % (inst.tags['Name'],inst.id,inst.state)	
			else:
				print "%s [%s]" % (inst.id,inst.state)

state = ['start','stop']
if args.i and args.s:
	if args.i not in all_Instances:
		print "Instance is not correct"
		sys.exit(0)
	elif args.s.lower() not in state:
		print "Invalid state value"
		sys.exit(0)
	elif args.s.lower() == 'start':
		instance_start(args.i)
	elif args.s.lower() == 'stop':
		instance_stop(args.i)

