#!/usr/bin/python
"""
	Boto instance class
	-------------------
This class handles,
	Starting a particular instance
	Stoping a particular instance 
	Displays all instances in a region along with the state of operation
"""
import boto.ec2

class InstanceAction():
    def __init__(self):
		self.region = null
		self.conn = null

	@classmethod
	def load_from_config(self, path):
		"""
		Load settings from a JSON config file
		And define all variables
		"""
		if path:
			config = ConfigParser.ConfigParser();
			config.read([path]);
			self.region = config.get("info", "ec2_region_name")
			self.conn = boto.ec2.connect_to_region(self.region)

	@classmethod
	def start_instance(self, instanceId):
		"""
		Start a particular Instance under particular region
		"""
		instance = self.check_instance(instanceId)
		if instance and instance.state == "stop":
			instance.start()
			
			
	@classmethod
	def check_instance(self, instanceId):
		"""
		To check whether the instance exists in a specific region
		"""
		if self.region and instanceId:
			reservations = self.conn.get_all_instances() 
			for r in reservations:
				for i in r.instances:
					if i.id == instanceId
						return i
			return null
			
	
	@classmethod
	def stop_instance(self, instanceId):
		"""
		Stop a particular InstanceId under particular region
		"""
		instance = self.check_instance(instanceId)
			if instance and instance.state == "running":
				instance.stop()

	
	@classmethod
	def display_all_instances(self):
		"""
		Displays all the instances
		"""
		reservations = self.conn.get_all_instances() 
			for r in reservations:
				for i in r.instances:
					print '{0}:{1}:{2}'.format(i, i.tags['Name'],i.state)


if __name__ == "__main__":
	i = InstanceAction()
	i.load_from_config("config.ini")
	
	
	

	

	
