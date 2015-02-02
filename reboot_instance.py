#!/usr/bin/python
"""
	python version- 2.7.6
	This class handles deregistering,restarting a instances and registering the 	instances to load balancer.
	Displays all instances in a region along with the state of operation.
"""
import sys
from pprint import pprint
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
		self.loadBalancers_fromconfig = [elbs.strip() for elbs in config.get("elbs","elb").split(",")]			
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
			self.elb = boto.ec2.elb.connect_to_region(self.region)
		except Exception, message:
			self.lgr.error(message)
			sys.exit(0)
		self.lgr.info("connected to region")

		#validate load balancers
		self.validate_loadBalancers()

		for lb in self.loadBalancers_fromconfig:
			load_balancer = self.elb.get_all_load_balancers(load_balancer_names=lb.split())[0]			
			for instance in load_balancer.instances:				
				#health check - in service
				if "InService" in str(load_balancer.get_instance_health(instance.id)):
					
					self.reboot_instance(instance.id)
					time.sleep(30)
					self.await_elb_instance_state(load_balancer, instance.id, 'OutOfService')
					time.sleep(20)
					self.await_elb_instance_state(load_balancer, instance.id, 'InService')
				else:
					self.lgr.info(instance.id + " Instance is out of service")
	
	#@classmethod	
	def await_elb_instance_state(self, lb, instanceId, awaited_state):
		"""
		wait for an ELB to change the state
		"""
		print instanceId
		while awaited_state not in str(lb.get_instance_health(instanceId)):
			time.sleep(20)
			self.lgr.info(instanceId + " Instance is waiting for " + awaited_state)
		self.lgr.info(instanceId + " Instance is back into " + awaited_state)

	#@classmethod
	def validate_loadBalancers(self):
		"""
		validate all load balancers with defined load balancers in conf file
		"""
		loadBalancers_throughApi = self.elb.get_all_load_balancers()
		elbs_names = [elbs.name for elbs in loadBalancers_throughApi]
		for lbs in self.loadBalancers_fromconfig:
			if lbs in elbs_names:
				self.lgr.info(lbs + " validated")
			else:
				self.lgr.info(lbs + " not validated")
				sys.exit(0)

	#@classmethod
	def reboot_instance(self, instanceId=None):
		"""
		rebooting a particular Instance under particular region
		"""
		if not instanceId:
			self.lgr.info("InstanceId is empty")
		self.lgr.info(instanceId + " is rebooting")
		try:
			check_rebooted = self.conn.reboot_instances(instanceId)
			if check_rebooted:
				self.lgr.info(instanceId + " is rebooted")
			else:
				self.lgr.info(instanceId + " not rebooted")				
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)
		#self.lgr.info(instanceId + " is rebooted")

# create object
i = InstanceAction()
i.elb_connection()
