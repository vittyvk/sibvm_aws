import subprocess
import requests
import boto3
import os
import sys
import yaml
import base64

ENCLAVE_SIZE="t3.micro"

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

    region = get_metadata("placement/region")
    availability_zone=get_metadata("placement/availability-zone")
    instance_id = get_metadata("instance-id")
    security_group = get_metadata("security-groups")
    public_key = get_metadata("public-keys").split("=")[1]
    ami = get_metadata("ami-id")
    nic1_mac = get_metadata("network/interfaces/macs/")
    nic1_subnet = get_metadata("network/interfaces/macs/%s/subnet-id" % nic1_mac)
    private_ip = get_metadata("local-ipv4")

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
                                     InstanceType=ENCLAVE_SIZE,
                                     KeyName=public_key,
                                     SubnetId=nic1_subnet,
                                     UserData=cloud_config)

    sib_ip = instances[0].private_ip_address
    print("Sibling VM created: %s" % sib_ip)
