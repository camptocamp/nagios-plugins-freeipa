#!/usr/bin/env python2

import cookielib
import json
import ssl
import urllib
import urllib2


def freeipa_login(login,password, baseurl, ca_file):
    url = baseurl + 'ipa/session/login_password'
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
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_verify_locations(ca_file)
        https_handler = urllib2.HTTPSHandler(context=context)
    except:
        https_handler = urllib2.HTTPSHandler()
    opener = urllib2.build_opener(redirect_handler, cookie_handler, https_handler)

    request = urllib2.Request(url, data, headers)
    response = opener.open(request)

    return (opener, cookies, response)

def freeipa_api_call(baseurl, api_vers, method, params, opener, cookies):
    url = baseurl + 'ipa/session/json'
    data = {
            'method' : method,
            'params' : [
                [],
                {
                    'version' : api_vers,
                },
            ],
            'id' : None,
    }
    headers = {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json',
            'Referer' : baseurl + 'ipa',
    }
    for param in params:
        data['params'][1][param] = params[param]
    data = json.dumps(data)

    request = urllib2.Request(url, data, headers)
    response = opener.open(request)

    return (opener, cookies, response)
