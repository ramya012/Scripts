#!/usr/bin/python

import json
import boto
import boto.vpc
import boto.ec2
import time
import sys
import logging
import os
import pprint
 
class create_env:
	environment = "test"
	vpcId = None
	gatewayId = None
	subnets_Created = {}
	rTables = {}
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
	
	#@classmethod	
	def createSubnet(self):
		subnets = self.confData['subnets']
		for i in subnets:
			subnet = i['ip_range']
			zone = i['zone']
			tagName = i['name']
			routeAssosciate = i['route_associate']
			exist = self.checkSubnet(subnet)
			#print exist
			if exist is None:
				s1 = self.conn.create_subnet(self.vpcId, subnet, zone)
				#print s1
				self.lgr.info("created the subnet"+ tagName)			
				time.sleep(2)
				s1.add_tag('Name', tagName)
				time.sleep(2)
			else:
				self.lgr.info("Already existed"+ tagName)
				s1 = exist
			#association
						
			self.subnets_Created[routeAssosciate] = s1.id
		#for item in self.subnets_Created:
		#	print item.id			
			
	#@classmethod
	def checkSubnet(self,sub):		
		subnet = self.conn.get_all_subnets(filters={"cidrBlock" : sub})
		if len(subnet):
			return subnet[0]
		else:
			return None
	
	#@classmethod
	def createRouteTable(self):
		routeTables = self.confData['route_tables']		
		
		check_Tables = self.conn.get_all_route_tables(filters={"vpc-id" : self.vpcId})[0]
		print(check_Tables['name'])
		#for table in check_Tables.routes:
		#	print(table)
		sys.exit(0)
		
		for name in routeTables:
			rt = self.conn.create_route_table(self.vpcId)
			rt.add_tag('Name',name)
			self.rTables[name] = rt.id		
		#print rTables
		
	def associateRouteWithSubnet(self):
		for name, id in self.subnets_Created.items():
			subnetId = id
			routeId = self.rTables[name]
			print routeId
			self.conn.associate_route_table(routeId, subnetId)
			
	
i = create_env()
i.get_VPCConnection()
i.createSubnet()
i.createRouteTable()
i.associateRouteWithSubnet()

