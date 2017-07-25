#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

#from urllib.parse import urlparse, urlencode
#from urllib.request import urlopen, Request
import urllib.request 
import urllib.parse 
import urllib.response
import http.cookiejar
from urllib.error import HTTPError

import httplib2
import json
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from pprint import pprint

import datetime

from flask import Flask, render_template
 
from flask import request
from flask import make_response

import time

# Flask app should start in global layout
app = Flask(__name__, static_url_path='/')

# Departments: treasury, private banking, corporate banking
# ChatBoot  -   GMAILCalendarJSON
# data      -   start.dateTime
#           -   end.dateTime = start.dateTime + 30 minut
# email     -   attendees.email


url = 'http://80.241.97.49:50000/sap/opu/odata/LMC/OLI_MOBILE_SRV/CZAT_TEST_SET'
userName = 'AISAP_TEST'
passWord = 'asyai.1'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    #res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/<string:page_name>')
def root(page_name):
    print("DUPA")   
    print(os.path.dirname(os.path.realpath(__file__)))

    return app.send_static_file(page_name)


def processRequest(req):
    print("processRequest")
    akcja = req.get("result").get("action") 
    #print(akcja)
    #print(Actions[akcja])
    if akcja in Actions:
        res = Actions[akcja](req)
    else:
        return {}
    return res

def sapLogin():
    # Tutaj zrobi sobie pytanie do SAPa
    
    cj = http.cookiejar.CookieJar()
    #opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    #r = opener.open("http://example.com/")
    
    passwordManager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passwordManager.add_password(None, url, userName, passWord);

    auth_handler = urllib.request.HTTPBasicAuthHandler(passwordManager)

    opener = urllib.request.build_opener(auth_handler, urllib.request.HTTPCookieProcessor(cj))

    urllib.request.install_opener(opener)
    return opener
    
def getResultParam(req, field):

    return req.get("result").get("parameters").get(field)

def getLicense(req):

    
    
    
    opener = sapLogin()
    
    result = askSap(opener, data=None)

    return result.read().decode('utf-8')


def getTest(req):
    print("GetTEST")
   
    opener = sapLogin()
    #data = urllib.parse.urlencode(values)

#     set-cookie: sap-usercontext=sap-client=005; path=/
#     set-cookie: SAP_SESSIONID_SD1_005=ka-wcYHeCK9olgbGGa6s0J-A-7RQTRHntmUAUFa7dK4%3d; path=/
#     content-type: application/atom+xml;type=feed; charset=utf-8
#     content-length: 10147
#     x-csrf-token: Wk5AWTREx1Hk7nXXF_z5mQ==
#     dataserviceversion: 2.0
#     sap-metadata-last-modified: Mon, 12 Jun 2017 13:42:10 GMT
#     cache-control: no-store, no-cache
# 


    tokenGet = askSap(opener, data=None, headers={'X-CSRF-Token': "Fetch"})

    for key, value in tokenGet.getheaders():
        print(key + ": " + value) 
    
    xcsrfToken = tokenGet.getheader('x-csrf-token', default=None)
    cookies = tokenGet.getheader('set-cookie', default=None)

    pprint(cookies)

    if xcsrfToken is None:
        return {}

    values = {
            "LicType"       : getResultParam(req, "License"),
            "TextLicType"   : getResultParam(req, "License"),
            "LicPurTotal"   : "2"
            }
   
    pprint(values)
    #data = str.encode(urllib.parse.urlencode(values), 'utf-8')
    data = str.encode(json.dumps(values), 'utf-8')

    time.sleep(2)

    pprint(data)
    headers = {
            'x-csrf-token': xcsrfToken,
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': len(data)
            }

    result = askSap(opener, data=data, headers=headers, method='POST')
    
    return result.read().decode('utf-8')


def askSap(opener, data=None, headers=None, method='GET'):

    request = urllib.request.Request(url, method=method)
    if headers is not None:
        for key in headers:
            request.add_header(key, headers[key])

    pprint(request.get_method())
    pprint(request.get_full_url())
    pprint(request.header_items())

    try:
        result = opener.open(request, data)
    except IOError as e:
        print (e)

    return result



Actions = {
    'get.licenses.list': getLicense,
    'getTest': getTest
}




if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ')),
    app.run(debug=True, port=port, host='0.0.0.0')
