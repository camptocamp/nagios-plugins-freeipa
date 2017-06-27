#!/usr/bin/env python2

import argparse
import cookielib
import datetime
import json
import ssl
import sys
import urllib
import urllib2


def freeipa_login(login,password):
    url = FREEIPA_SERVER_BASEURL + 'ipa/session/login_password'
    opts = {
            'user' : login,
            'password' : password,
    }
    headers = {
            'Accept' : 'text/plain',
            'Content-Type' : 'application/x-www-form-urlencoded',
    }
    data = urllib.urlencode(opts)
    cookies = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor( cookies )
    redirect_handler = urllib2.HTTPRedirectHandler()
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_verify_locations(FREEIPA_CA_FILE)
    https_handler = urllib2.HTTPSHandler(context=context)
    opener = urllib2.build_opener(redirect_handler, cookie_handler, https_handler)

    request = urllib2.Request(url, data, headers)
    response = opener.open(request)

    return (opener, cookies, response)

def freeipa_api_call(method, params, opener, cookies):
    url = FREEIPA_SERVER_BASEURL + 'ipa/session/json'
    data = {
            'method' : method,
            'params' : [
                [],
                {
                    'version' : FREEIPA_API_VERS,
                },
            ],
            'id' : None,
    }
    headers = {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json',
            'Referer' : FREEIPA_SERVER_BASEURL + 'ipa',
    }
    for param in params:
        data['params'][1][param] = params[param]
    data = json.dumps(data)

    request = urllib2.Request(url, data, headers)
    response = opener.open(request)

    return (opener, cookies, response)

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="host to connect to", required=True)
parser.add_argument("--username", help="freeIPA username", required=True)
parser.add_argument("--password", help="freeIPA password", required=True)
parser.add_argument("--ca", help="freeIPA ca file", default="/etc/ipa/ca.crt")
parser.add_argument("--api-version", help="freeIPA API version", default="2.156")
parser.add_argument("--verbose", "-v", help="Toggle verbose mode", action="store_true")
parser.add_argument("--span", "-s", help="Time span", type=int, default=30)

args = parser.parse_args()

FREEIPA_CA_FILE = args.ca
FREEIPA_SERVER_BASEURL = 'https://%s/' % args.host
FREEIPA_API_VERS = args.api_version
VERBOSE = args.verbose
TIME_SPAN = args.span

try:
    (url_opener, cookies, response) = freeipa_login(args.username, args.password)
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
(url_opener, cookies, response) = freeipa_api_call('cert_find', params, url_opener, cookies)
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
