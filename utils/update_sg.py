import boto3
from botocore.config import Config

sgs=[ 	{"zone": "us-east-1", "sg": "sg-00c851f471a572f01"},
	{"zone": "eu-central-1", "sg": "sg-0c7efff621df44fd3"},
	{"zone": "ap-northeast-1", "sg": "sg-082100e938b500c7a"}]

for sg in sgs:
	my_config = Config(
		region_name = sg["zone"],
		signature_version = 'v4',
		retries = {
			'max_attempts': 2,
			'mode': 'standard'
		}
	)

	ec2 = boto3.resource('ec2',config=my_config)
	group = ec2.SecurityGroup(sg["sg"])
	print("Zone:"+sg["zone"])
	print("Before:")
	for perml in group.ip_permissions:
		for perm in perml:
			print(str(perm)+":"+str(perml.get(perm))+" ",end="")
		print("\n")
	try:
		response=group.authorize_ingress(IpPermissions=[{
			'IpProtocol':'6',
				'FromPort':5201,
				'ToPort':5210,
				'IpRanges': [{
					'CidrIp':'0.0.0.0/0'
				}]
		}])
	except:
		print("Rule already exists")
	group.load()
	print("After:")
	for perml in group.ip_permissions:
		for perm in perml:
			print(str(perm)+":"+str(perml.get(perm))+" ",end="")
		print("\n")


