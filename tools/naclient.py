#!/usr/bin/env python3

import urllib.request
import urllib.parse
import json
import sys
import argparse

parser=argparse.ArgumentParser()

for argv in sys.argv:
    if argv.startswith('-'):
        parser.add_argument(argv, nargs='?', const='')

if '-pyname' not in sys.argv:
    print("-pyname (pyname) Argument is required")
    sys.exit(2)
# pyname = argv.n

if '-pyhost' not in sys.argv:
    print("-pyhost (Remote host) Argument is required")
    sys.exit(2)
if '-pyport' not in sys.argv:
    print("-pyport (Remote pyport) Argument is required")
    sys.exit(2)

args = vars(parser.parse_args())
send = {}
host = ""
port = ""
key = ""

n = ""
q = ""

for k, v in args.items():
    if k == "pyhost":
        host = args["pyhost"]
    elif k == "pyport":
        port = args["pyport"]
    elif k == "pykey":
        key = args["pykey"]
    elif k == "pyname":
        a = args["pyname"].split()
        n = a[0]
        q = " ".join(a[1:])

send[n]=q

try:
    data=json.dumps(send)
    req = urllib.request.Request("http://" + host + ":" + port + "/nag")
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    if key != "":
        req.add_header('Apikey', key)
    jsondataasbytes = data.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', str(len(jsondataasbytes)))
    response = urllib.request.urlopen(req, jsondataasbytes)
    respdata = response.read()
    encoding = response.info().get_content_charset('utf-8')
    respjson = json.loads(respdata.decode(encoding))
except Exception as e:
    print(e)
    sys.exit(2)

for k, v in respjson.items():
    print(v)
    if k == "OK":
        sys.exit(0)
    elif k == "WARNING":
        sys.exit(1)
    elif k == "CRITICAL":
        sys.exit(2)
    else:
        sys.exit(3)

