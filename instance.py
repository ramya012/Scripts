#!/usr/bin/python
"""
	Boto instance class
	-------------------
This class handles,
	Starting a particular instance
	Stoping a particular instance 
	Displays all instances in a region along with the state of operation
"""
import sys
import boto.ec2
import ConfigParser
import logging
import os
import time

class InstanceAction:
	def __init__(self):
		"""
		Creating a logger and file handler
		"""
		self.lgr = logging.getLogger('MyLogger')
		self.lgr.setLevel(logging.DEBUG)
		fh = logging.FileHandler('instanceLogger.log')
		self.lgr.addHandler(fh)
		self.load_from_config("config.ini")
		print self.region

	#@classmethod
	def load_from_config(self, path=None):
		"""
		Load settings from a JSON config file 
		And define all variables
		"""
		#checking the path is empty or not
		if not path:
			self.lgr.info("Path for ini file is empty")
			sys.exit(0)			
		config = ConfigParser.ConfigParser()
		#checking whether file exists or not
		if not os.path.isfile(path):
			self.lgr.error("unable to find required ini file "+str(path))
			sys.exit(0)
		config.read([path])
		self.region = config.get("Region", "ec2_region_name")
		#connecting to region
		try:
			self.conn = boto.ec2.connect_to_region(self.region)
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)
		self.lgr.info("connected to "+ str(self.region))

	#@classmethod
	def start_instance(self, instanceId=None):
		"""
		Start a particular Instance under particular region
		"""
		if not instanceId:
			self.lgr.info("InstanceId is empty")
		try:
			instances = self.conn.start_instances(instance_ids = instanceId)
			for instance in instances:
				while instance.state != 'running':
					self.lgr.info("Waiting for instances to run: " + str(instance.id))
					time.sleep(4)
					instance.update()
			self.lgr.info("Instance started"+ str(instance.id))	
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)

	#@classmethod
	def stop_instance(self, instanceId=None):
		"""
		Stop a particular Instance under particular region
		"""
		if not instanceId:
			self.lgr.info("InstanceId is empty")
		try:
			instances = self.conn.stop_instances(instance_ids = instanceId)
			for instance in instances:
				while instance.state != 'stopped':
					self.lgr.info("Waiting for instances to stopping " + str(instance.id))
					time.sleep(4)
					instance.update()
			self.lgr.info("Instance stopped "+ str(instance.id))	
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)
				
i = InstanceAction()
i.stop_instance("i-dc763931")
	
	
	

	

	
