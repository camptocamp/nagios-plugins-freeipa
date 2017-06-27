#!/usr/bin/env python2

import argparse
import datetime
import sys
from lib import *

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="host to connect to", required=True)
parser.add_argument("--username", help="freeIPA username", required=True)
parser.add_argument("--password", help="freeIPA password", required=True)
parser.add_argument("--ca", help="freeIPA ca file", default="/etc/ssl/certs/ca-certificates.crt")
parser.add_argument("--api-version", help="freeIPA API version", default="2.156")
parser.add_argument("--verbose", "-v", help="Toggle verbose mode", action="store_true")
parser.add_argument("--span", "-s", help="Time span", type=int, default=30)

args = parser.parse_args()

FREEIPA_SERVER_BASEURL = 'https://%s/' % args.host
VERBOSE = args.verbose
TIME_SPAN = args.span

try:
    (url_opener, cookies, response) = freeipa_login(args.username, args.password, FREEIPA_SERVER_BASEURL, args.ca)
    if response.getcode() != 200:
        sys.exit(2)
except urllib2.HTTPError as e:
    print("Critical: got error code %i upon login" % e.getcode())
    sys.exit(2)
    
start = datetime.datetime.now()
end = start + datetime.timedelta(+TIME_SPAN)
params = {
        'validnotafter_from': start.strftime('%Y-%m-%d'),
        'validnotafter_to':   end.strftime('%Y-%m-%d'),
        'all':                True,
        }
(url_opener, cookies, response) = freeipa_api_call(FREEIPA_SERVER_BASEURL, args.api_version,'cert_find', params, url_opener, cookies)
resp = json.load(response)
if resp['error']:
    print('Critical: %s' % resp['error']['message'])
    sys.exit(2)

if resp['result']['count'] != 0:
    print('Critical: %s IPA certificates will blow in next %i days' % (resp['result']['count'], TIME_SPAN))
    if VERBOSE:
        for result in resp['result']['result']:
            print('Cert: %s - Valide until: %s' %(result['subject'], result['valid_not_after']))
    sys.exit(2)
print('OK: IPA Cert validity')
sys.exit(0)
