import os
import sys
import boto3
import requests

def get_metadata(path):
    try:
        r = requests.get("http://169.254.169.254/latest/meta-data/%s" % path, timeout=2)
        if r.status_code != 200:
            print("Failed to get %s metadata!" % path, file=sys.stderr)
            sys.exit(1)
    except:
            print("Failed to get %s metadata!" % path, file=sys.stderr)
            sys.exit(1)
    return r.text

def get_ec2():
    region = get_metadata("placement/region")

    if not "AWS_ACCESS_KEY" in os.environ:
        print("Please set AWS_ACCESS_KEY environment variable)", file=sys.stderr)
        sys.exit(1)
    if not "AWS_SECRET_KEY" in os.environ:
        print("Please set AWS_SECRET_KEY environment variable)", file=sys.stderr)
        sys.exit(1)

    access_key = os.environ["AWS_ACCESS_KEY"]
    secret_key = os.environ["AWS_SECRET_KEY"]

    ec2 = boto3.resource("ec2", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    return ec2

def get_instances():
    ec2 = get_ec2()

    main_instance_id = get_metadata("instance-id")

    instances = ec2.instances.filter(
    Filters=[{'Name': 'tag:MainVM', 'Values': [main_instance_id]}])

    return instances
