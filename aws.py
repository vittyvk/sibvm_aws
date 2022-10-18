import sys
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
