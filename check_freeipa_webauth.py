#!/usr/bin/env python2

import argparse
import json
from lib import *

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="host to connect to", required=True)
parser.add_argument("--username", help="freeIPA username", required=True)
parser.add_argument("--password", help="freeIPA password", required=True)
parser.add_argument("--ca", help="freeIPA ca file", default="/etc/ipa/ca.crt")
parser.add_argument("--api-version", help="freeIPA API version", default="2.156")

args = parser.parse_args()

FREEIPA_SERVER_BASEURL = 'https://%s/' % args.host

try:
    (url_opener, cookies, response) = freeipa_login(args.username, args.password, FREEIPA_SERVER_BASEURL, args.ca)
    if response.getcode() != 200:
        sys.exit(2)
except urllib2.HTTPError as e:
    print "Critical: got error code %i upon login" % e.getcode()
    sys.exit(2)
    
(url_opener, cookies, response) = freeipa_api_call(FREEIPA_SERVER_BASEURL, args.api_version, 'ping', '', url_opener, cookies)
resp = json.load(response)
if resp['error']:
    print 'Critical: %s' % resp['error']['message']
    sys.exit(2)


print 'OK: service is working as expected'
sys.exit(0)
