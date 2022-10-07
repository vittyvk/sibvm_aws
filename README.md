# Create a sibling VM on AWS and make it an encalve

## About

This is a sample python script which is supposed to be launched from an AWS
instance. It creates a 'sibling' instance in the same availability zone and
the same network as the main VM, isolates the instance with iptables and launch
a sample echo server (borrowed from https://realpython.com/python-sockets/) on
port 8080.

## Usage

- Launch a RHEL8 instance
- yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
- yum -y install python3 python3-boto3 git netcat
- git clone https://github.com/vittyvk/sibvm_aws.git
- cd sibvm_aws
- export AWS_ACCESS_KEY=xxxx
- export AWS_SECRET_KEY=yyyy
- python3 ./sibvm_aws.py

You are suposed to see:

>
> Sibling VM created: 10.1.111.51
>

Give the vm some time to boot and then do:

> $ nc 10.1.111.51 8080  
> 1245  
> Hello from enclave! You wrote: 1245  

## License

GNU GPLv2+
