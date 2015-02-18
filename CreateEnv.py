#!/usr/bin/python

import json
import boto
import boto.vpc
import boto.ec2
import time
import sys
import logging
import os
 
class create_env:
	environment = "test"
	vpcId = None
	gatewayId = None
	def __init__(self):
		self.lgr = logging.getLogger('MyLogger')
		self.lgr.setLevel(logging.DEBUG)
		file_handler = logging.FileHandler('Ditech.log')
		self.lgr.addHandler(file_handler)
		self.load_from_config("config.json")

	#@classmethod
	def load_from_config(self, path=None):
		"""
		Load settings from a json file 
		And define all variables
		"""
		#checking the path is empty or not
		if not path:
			self.lgr.info("Path for json file is empty")
			sys.exit(0)
		
		#checking whether file exists or not
		if not os.path.isfile(path):
			self.lgr.error("unable to find required json file "+str(path))
			sys.exit(0)

		with open(path,"r") as fp:
			input = json.load(fp)
		
		self.confData = input[self.environment]
		# load all required fields
		region = self.confData['region']
			
		#connecting to region
		try:
			self.conn = boto.vpc.connect_to_region(region)
		except Exception, message:
			self.lgr.error(str(message))
			sys.exit(0)
		self.lgr.info("connected to "+ str(region))

	def get_VPCConnection(self):
		vpcCidr = self.confData['VPC_Cidr']			
		try:
			vpc = self.conn.get_all_vpcs(filters={'cidrBlock': vpcCidr})
			if not len(vpc):
				self.createVPC()
			else:
				self.vpcId = vpc[0].id
				gateway = self.conn.get_all_internet_gateways(filters={'attachment.vpc-id':self.vpcId})
				if not len(gateway):
					self.createGateway()
				else:
					self.gatewayId = gateway[0].id
		except Exception, message:
			self.lgr.error(str(message))

	def createVPC(self):
		vpcCidr = self.confData['VPC_Cidr']	
		account = self.confData['account']
		region = self.confData['region']
		vpc = self.conn.create_vpc(vpcCidr)
		vpcName = account + '_' + region.upper()
		vpc.add_tag('Name',vpcName)
		self.vpcId = vpc.id
		self.createGateway()

	def createGateway(self):
		if self.vpcId:
			igw = self.conn.create_internet_gateway()
			self.gatewayId = igw.id
			time.sleep(4)
			self.conn.attach_internet_gateway(self.gatewayId,self.vpcId)
		else:
			self.createVPC()
	"""
	def createRouteTable(self):
		route = self.conn.create_route_table(self.vpcId)
		self.conn.create_route(route.id,'0.0.0.0/0',self.gatewayId)
		route.add_tag
	"""
	def createSubnet(self):
		subnets = self.confData['subnets']
		for i in subnets:
			subnet = i['ip_range']
			zone = i['zone']
			tagName = i['name']
			s1 = self.conn.create_subnet(self.vpcId, subnet, zone)
			self.lgr.info("created the subnet"+ tagName)			
			time.sleep(2)
			s1.add_tag('Name', tagName)
			time.sleep(2)
			


i = create_env()
i.get_VPCConnection()
i.createSubnet()
