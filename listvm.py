#! /usr/bin/python3

import aws

if __name__ == '__main__':
    for instance in aws.get_instances():
        if instance.state['Name'] != "terminated":
            print(instance.id, instance.instance_type)
