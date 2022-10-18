#! /usr/bin/python3

import sys
import aws
import getopt

def usage(retcode):
    print("%s [-a] [-h] [-v] [<instance-id>] [<instance-id>] ..." % sys.argv[0])
    sys.exit(retcode)

if __name__ == '__main__':
    killall = False
    verbose = False
    instanceid = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahv", ["all", "help", "verbose"])
    except getopt.GetoptError:
        usage(2)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            usage(0)
        if opt in ('-a', "--all"):
            killall = True
        if opt in ('-v', "--verbose"):
            verbose = True

    if args == [] and not killall:
        usage(1)

    for instance in aws.get_instances():
        if killall or instance.id in args:
            if verbose:
                   print("terminating instance.id %s" % instance.id)
            instance.terminate()
