import subprocess
import boto3
import os
import sys
import yaml
import base64
import getopt
import aws

def usage(retcode):
    print("%s [-h] <instance-type>" % sys.argv[0])
    sys.exit(retcode)

if __name__ == '__main__':
    if not "AWS_ACCESS_KEY" in os.environ:
        print("Please set AWS_ACCESS_KEY environment variable)", file=sys.stderr)
        sys.exit(1)
    if not "AWS_SECRET_KEY" in os.environ:
        print("Please set AWS_SECRET_KEY environment variable)", file=sys.stderr)
        sys.exit(1)

    access_key = os.environ["AWS_ACCESS_KEY"]
    secret_key = os.environ["AWS_SECRET_KEY"]

    ssh_keyfile = "%s/.ssh/id_rsa" % os.environ['HOME']

    if not os.path.exists(ssh_keyfile):
        subprocess.run(["ssh-keygen", "-f", ssh_keyfile, "-t", "rsa", "-b", "2048", "-P", ""])

    try:
        with open(ssh_keyfile + ".pub", 'r') as f:
            ssh_pubkey = f.readlines()[0][:-1]
    except:
        print("Failed to read SSH public key from ~/.ssh/id_rsa.pub")
        sys.exit(1)

    try:
        with open("helloserver.py", 'rb') as f:
            hello_py = f.read()
    except:
        print("Failed to read helloserver.py")
        sys.exit(1)

    try:
        with open("helloserver.service", 'rb') as f:
            hello_service = f.read()
    except:
        print("Failed to read helloserver.service")
        sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError:
        usage(2)

    for opt, arg in opts:
        if opt == 'h':
            usage(0)

    if args == []:
        usage(2)

    instance_size = args[0]

    region = aws.get_metadata("placement/region")
    availability_zone = aws.get_metadata("placement/availability-zone")
    instance_id = aws.get_metadata("instance-id")
    security_group = aws.get_metadata("security-groups")
    public_key = aws.get_metadata("public-keys").split("=")[1]
    ami = aws.get_metadata("ami-id")
    nic1_mac = aws.get_metadata("network/interfaces/macs/")
    nic1_subnet = aws.get_metadata("network/interfaces/macs/%s/subnet-id" % nic1_mac)
    private_ip = aws.get_metadata("local-ipv4")
    main_instance_id = aws.get_metadata("instance-id")

    # Debug: create a user
    # "users": [{"name":"test",
    #                              "ssh-authorized-keys": [ssh_pubkey],
    #                              "groups": "wheel",
    #                              "sudo": "ALL=(ALL) NOPASSWD:ALL"
    #                              }
    #                             ],
    # Don't forget to unmask SSH port in iptables!

    cloud_config_data={"packages": ["iptables", "python3"],
                       "write_files": [{"encoding": "b64",
                                        "owner": "root:root",
                                        "permissions": "0755",
                                        "path": "/run/helloserver.py",
                                        "content": base64.b64encode(hello_py)
                                        },
                                       {"encoding": "b64",
                                        "owner": "root:root",
                                        "permissions": "0644",
                                        "path": "/etc/systemd/system/helloserver.service",
                                        "content": base64.b64encode(hello_service)
                                        }
                                       ],
                       "runcmd": ["iptables -A INPUT ! -s %s -j DROP" % private_ip,
                                  "iptables -A INPUT -p tcp --destination-port 8080 -j ACCEPT",
                                  "iptables -I INPUT -p tcp -j DROP"
                                  "systemctl daemon-reload",
                                  "systemctl start helloserver"
                                  ]
                       }
    cloud_config =  "#cloud-config" + "\n" + yaml.dump(cloud_config_data)

    ec2 = boto3.resource("ec2", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    instances = ec2.create_instances(ImageId=ami,
                                     Placement={'AvailabilityZone': availability_zone},
                                     MinCount=1,
                                     MaxCount=1,
                                     InstanceType=instance_size,
                                     KeyName=public_key,
                                     SubnetId=nic1_subnet,
                                     UserData=cloud_config,
                                     TagSpecifications=[{'ResourceType': 'instance',
                                                         'Tags': [{"Key": "MainVM", "Value": main_instance_id}]}]
                                     )

    sib_ip = instances[0].private_ip_address
    print("Sibling VM created: %s" % sib_ip)
