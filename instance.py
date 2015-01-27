#!/usr/bin/python
"""
	Boto instance class
	-------------------
	This class handles deregistering,restarting a instances and registering the 	instances to load balancer.
	Displays all instances in a region along with the state of operation.
"""
import sys
import boto.ec2
import ConfigParser
import logging
import os
import time
import boto.ec2.elb
import boto.utils

class InstanceAction:
	def __init__(self):
		"""
		Creating a logger and file handler
		"""
		self.lgr = logging.getLogger('MyLogger')
		self.lgr.setLevel(logging.DEBUG)
		file_handler = logging.FileHandler('instanceLogger.log')
		self.lgr.addHandler(file_handler)
		self.load_from_config("config.ini")
		
	#@classmethod
	def load_from_config(self, path=None):
		"""
		Load settings from a config file 
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
		# load all required fields
		self.region = config.get("Region", "ec2_region_name")
		self.loadBalancers = [elbs.strip() for elbs in config.get("elbs","elb").split(",")]			
		#connecting to region
		try:
			self.conn = boto.ec2.connect_to_region(self.region)
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)
		self.lgr.info("connected to "+ str(self.region))

	#@classmethod
	def elb_connection(self):
		"""
		Connecting a specific elastic load balnacer in the specified region
		"""
		try:
			elb = boto.ec2.elb.connect_to_region(self.region)
		except Exception, message:
			self.lgr.error(message)
			sys.exit(0)
		self.lgr.info("connected to region")
		for lb in self.loadBalancers:
			load_balancer = elb.get_all_load_balancers(load_balancer_names=lb.split())[0]
			for instance in load_balancer.instances:				
				#health check - in service
				if "InService" in str(load_balancer.get_instance_health(instance.id)):
					load_balancer.deregister_instances(instance.id)
					self.lgr.info(instance.id + " deregistered")
					self.boot_instance(instance.id)
					time.sleep(10)
					load_balancer.register_instances(instance.id)
					self.lgr.info(instance.id + " registered")
					time.sleep(10)
					while "InService" not in str(load_balancer.get_instance_health(instance.id)):						
						self.lgr.info(instance.id)
						time.sleep(10)
					self.lgr.info(instance.id + "Instance back into Inservice")	
				else:
					self.lgr.info(instance.id + "Instance is out of service")

	#@classmethod
	def boot_instance(self, instanceId=None):
		"""
		rebooting a particular Instance under particular region
		"""
		if not instanceId:
			self.lgr.info("InstanceId is empty")
		self.lgr.info(instanceId + " is rebooting")
		try:
			instances = self.conn.reboot_instances(instance_ids = instanceId)
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)
		self.lgr.info(instanceId + " is rebooted")

# create object
i = InstanceAction()
i.elb_connection()
