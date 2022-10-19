# Create a sibling VM (on AWS)

## About

This is a sample python script which is supposed to be launched from an AWS
instance. It creates a 'sibling' instance in the same availability zone and
the same network as the main VM. When creating an 'enclave' ('-e' option to
'newvm.py)', the script isolates the instance with iptables and launches
a sample echo server (borrowed from https://realpython.com/python-sockets/) on
port 8080. In non-enclave mode, ssh public key of the current user is added
to 'ec2-user' in the remote VM to allow instant access.

## Usage

### Setup

- Launch a RHEL8 instance
- yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
- yum -y install python3 python3-boto3 git netcat
- git clone https://github.com/vittyvk/sibvm_aws.git
- cd sibvm_aws
- export AWS_ACCESS_KEY=xxxx
- export AWS_SECRET_KEY=yyyy

### Creating a VM

- ./newvm.py

You are suposed to see:

>
> Sibling VM created: 10.1.111.51
>

Give the vm some time to boot and then do:

$ ssh 10.1.111.51

### Creating an 'enclave' with an example 'echo' service

- ./newvm.py -e

You are suposed to see:

>
> Sibling VM created: 10.1.55.106
>

Give the vm some time to boot and then do:

> $ nc 10.1.55.106 8080
> 1245  
> Hello from enclave! You wrote: 1245  

### Listing all VMs

$ ./listvm.py  
i-062291e69965128f8 t3.small  

### Killing VMs

Killing an individual VM:  
$ ./killvm.py i-062291e69965128f8  

Killing all VMs:  
$ ./killvm.py -a  

## License

GNU GPLv2+
