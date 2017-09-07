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
from flask import jsonify

import time

# Flask app should start in global layout
app = Flask(__name__, static_url_path='/')

# Departments: treasury, private banking, corporate banking
# ChatBoot  -   GMAILCalendarJSON
# data      -   start.dateTime
#           -   end.dateTime = start.dateTime + 30 minut
# email     -   attendees.email

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'spreadsheet-python.json'
APPLICATION_NAME = 'GoogleSheet'
#GOOGLEMAPS_KEY = 'AIzaSyDfz3rsgtrZ3pymjhMyz9CJeLAU7yfR5SI'
#SHEETID = '1k_Nj1JBDcjScQzAIr2ID3zj1xyWsADFqtIaSp5YV9RE'
SHEETID = '179hCtu13Divv0vMU5J0M-j6clcS9meMmPRyJ9te92xA'

sapurl = 'http://80.241.97.49:50000/sap/opu/odata/LMC/OLI_MOBILE_SRV/CZAT_TEST_SET'
userName = 'AISAP_TEST'
passWord = 'asyai.1'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/querytext', methods=['POST'])
def queryText():
    req = request.get_json(silent=True, force=True)

    print("Querytext:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)
    #res = { "result": "DUPA" }

    #res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/slackevents', methods=['POST'])
def slackEvents():
    req = request.get_json(silent=True, force=True)

    print("SlackEvent:")
    print(json.dumps(req, indent=4))

    if ("challange" in req):
        res = slackverify(req)
    else:
        res = slacksafe(req)
    #res = { "result": "DUPA" }

    res = json.dumps(res, indent=4)
    #print(res)
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
    print(akcja)
    #print(Actions[akcja])

    if ("resolvedQuery" in req.get("result") and (req.get("result").get("resolvedQuery") == "HI" or req.get("result").get("resolvedQuery") == "RECAPS" )):
        return defaultIntent(req)

    if akcja in Actions:
        res = Actions[akcja](req)
    else:
        return {}
    return res

def slacksafe(req):
    print("Slack Save")
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    qdir = os.path.join(script_dir, req.get("api_app_id"), req.get("team_id"), req.get("token"))

    if (not os.path.isdir(qdir)):
        os.makedirs(qdir, mode=0o777, exist_ok=True)

    qfile = os.path.join(qdir, 'slack.txt')

    slackMessage = getSlackUsername(req.get("event").get("user")) + "</br>" + str.encode(req.get("event").get("text").replace('\n', '</br>'), 'utf-8')

    with open(qfile, "a") as myfile:
        myfile.write(slackMessage)

    return "OK" 

def getSlackUsername(username):
    # TODO decode SlackUserID to real Username
    return username

def slackverify(req):
    print("SlackVerify")
    result = { "challenge" : "OK" } #req.get("challenge") }
    
    #print(result)
    return result

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    credential_dir = os.path.join(script_dir, 'credentials')
    #print("Credential dir: %s" % credential_dir)
#    if not os.path.exists(credential_dir):
#        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.json')

    #print("Credential path: %s" % credential_path)
    store = Storage(credential_path)
    #print("Storage: %s" % credential_path)
    credentials = store.get()
    #print("store.get()")
    if not credentials or credentials.invalid:
        secret_path = os.path.join(credential_dir, CLIENT_SECRET_FILE)
        flow = client.flow_from_clientsecrets(secret_path, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def gmailLogin():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    print("Gmail Login")
    credentials = get_credentials()
    print("Authorization")
    http = credentials.authorize(httplib2.Http())
    print("Http poszlo")
    #return discovery.build('calendar', 'v3', http=http)
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

def generateAvailableSpeach(speech, stepTime, event):
    
    if (stepTime + datetime.timedelta(minutes = meetingTime) <= datetime.datetime.strptime(event.get("start").get("dateTime")[:19], '%Y-%m-%dT%H:%M:%S')):
        if (speech != ""):
            speech += " and "

        speech += "%s - %s" % (datetime.datetime.strftime(stepTime, '%H:%M'), event.get("start").get("dateTime")[11:16])

    return (speech, datetime.datetime.strptime(event.get("end").get("dateTime")[:19], '%Y-%m-%dT%H:%M:%S'))

def returnSpeech(speech, displayText=None, contexts=[], followUpEvent={}):
    if (displayText is None):
        displayText = speech

    result = {
        "speech": speech,
        "displayText": displayText,
        "contextOut": contexts,
        "source": "webhook-createEvent"
    }

#    {
#        "followupEvent": {
#            "name": "<event_name>",
#            "data": {
#                "<parameter_name>":"<parameter_value>>"
#            }
#        }
#    }

    if len(followUpEvent) > 0:
        result["followupEvent"] = followUpEvent

    return result

def getParam(req, field):
    if (field in req.get("result").get("parameters")):
        if (type(req.get("result").get("parameters").get(field)) is list):
            return ", ".join(req.get("result").get("parameters").get(field))
        else:
            return req.get("result").get("parameters").get(field)
    return None

def getSParam(req, field):
    result = getParam(req, field)
    if result is None:
        return ""

    return result

def getContextParam(req, name, field):
    for context in req.get("result").get("contexts"):
        if context.get("name") == name:
            print(type(context.get("parameters").get(field)))
            if (field in context.get("parameters")):
                if (type(context.get("parameters").get(field)) is list):
                    return ", ".join(context.get("parameters").get(field))
                elif (type(context.get("parameters").get(field)) is dict):
                    return getStrFromDict(context.get("parameters").get(field))
                else:
                    return context.get("parameters").get(field)

    return None

def getStrFromDict(value):
    result = ""
    for key in value:
        result += "%s " % value[key]

    return result

def removeMeeting(req):
    
    print("removeMeeting")
    #"date": "2017-05-13T15:00:00Z", 
    #         %Y-%m-%dT%H:%M:%SZ"

    service = gmailLogin()
    # Check Department
    calendars = getCalendarsFromDepartment(service, req.get("result").get("parameters").get("department"))
    pprint(calendars)

    for calendar in calendars:
        page_token = None
        while True:
            events = service.events().list(calendarId=calendar["id"], pageToken=page_token).execute()
            for event in events['items']:
                #print("Delete event:" + event["summary"])
                service.events().delete(calendarId=calendar["id"], eventId=event["id"]).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    speech = 'Events are deleted'
    
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-deleteEvents"
    }


def prepareHeaders(req):
    print("Create Headers")
    value_range_body = {
        "values": [
            [ 
                "Deal #", "Deal Date", "Buyer", "Seller", "StartDate", "EndDate", "Quantity", "QuantityUnit", "Price", "Currency", "Location"
            ]
        ]

    }

    appendRow(req, value_range_body)

    speech = "Headers are created"

    return returnSpeech(speech)

def createBloterConv(req):

    if req.get("result").get("actionIncomplete") == True:
        return returnSpeech(req.get("result").get("fulfillment").get("speech"))

    return createRow(req)

def getMaxDate(req, field):
    dateArray = getDateArray(req.get("result").get("parameters").get(field))

    result = None

    for test in dateArray:
        print(test)
        print(type(test))
        if result is None:
            result = test
        else:
            if result < test:
                result = test

    if result is None:
        return ""
    else:
        return datetime.datetime.strftime(result, '%d.%m.%Y')

def getMinDate(req, field):
    dateArray = getDateArray(req.get("result").get("parameters").get(field))

    result = None

    for test in dateArray:
        print(test)
        print(type(test))
        if result is None:
            result = test
        else:
            if result > test:
                result = test

    if result is None:
        return ""
    else:
        return datetime.datetime.strftime(result, '%d.%m.%Y')

def getDateArray(oneArray):
    dateArray = []
    testDate = None

    for one in oneArray:
        testDate = one.split('/')
        for second in testDate:
            dateArray.append(datetime.datetime.strptime(second, '%Y-%m-%d'))
    
    return dateArray

def getMaxNumber(req, field):
    testOne = None

    for one in req.get("result").get("parameters").get(field):
        if (testOne is None) or testOne < one:
            testOne = one

    if testOne is None:
        return ""
    else:
        return testOne

def getMinNumber(req, field):
    testOne = None

    for one in req.get("result").get("parameters").get(field):
        if (testOne is None) or testOne > one:
            testOne = one

    if testOne is None:
        return ""
    else:
        return testOne


def createRow(req):
    print("Create ROW")

    #createConv(req)
    if ("resolvedQuery" in req.get("result") and (req.get("result").get("resolvedQuery") == "HI" or req.get("result").get("resolvedQuery") == "conversation_event")):
        return returnSpeech("NORMAL CONVERSATION")

    if ("resolvedQuery" in req.get("result") and (req.get("result").get("resolvedQuery") == "RECAPS" or req.get("result").get("resolvedQuery") == "extractEntities_event")):
        return returnSpeech("Get RECAPS")


    #if req.get("result").get("actionIncomplete") == True:
    #    return returnSpeech(req.get("result").get("fulfillment").get("speech"))

    dealNr = "%f" % time.time()

    value_range_body = {
        "values": [
            [ 
                dealNr[:10],                                    # Deal Number
                datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y'), # Current Date
                getSParam(req, "buyer"),        # Buyer
                getSParam(req, "trader"),       # Seller
                getMinDate(req, "date-period"),    # StartDate
                getMaxDate(req, "date-period"),    # EndDate
                getMaxNumber(req, "number1"),     # Quantity
                getSParam(req, "quantityunit"), # QuantityUnit
                getMinNumber(req, "number1"),        # Price
                #getSParam(req, "currency"),     # Currency
                "GBP",                          # Currency
                getSParam(req, "location")      # Location
            ]
        ]

    }

    appendRow(req, "Arkusz1!A1", value_range_body)

    speech = "Added"

    #return returnSpeech(req.get("result").get("fulfillment").get("speech"))
    return returnSpeech(speech)



def createConv(req):
    
    client = "Client: " + req.get("result").get("resolvedQuery") + "\n"
    bot = "Bot: " + req.get("result").get("fulfillment").get("speech") + "\n"
    
    with open("conv.txt", "a") as myfile:
        myfile.write(client)
        myfile.write(bot)

    return returnSpeech(req.get("result").get("fulfillment").get("speech"))


def createConversation(req):
    print("Create Conv")
    value_range_body = {
        "values": [
            [ 
                "Client:", req.get("result").get("resolvedQuery")
            ],
            [
                "Bot:", req.get("result").get("fulfillment").get("speech")
            ]
        ]

    }

    appendRow(req, "Arkusz2!A1", value_range_body)

    return returnSpeech(req.get("result").get("fulfillment").get("speech"))


def appendRow(req, sheetRange, values):
    print("Append ROW")

    service = gmailLogin()

    # The A1 notation of a range to search for a logical table of data.
    # Values will be appended after the last row of the table.
    range_ = sheetRange  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'RAW'  # TODO: Update placeholder value.

    # How the input data should be inserted.
    insert_data_option = 'INSERT_ROWS'  # TODO: Update placeholder value.
    # "parameters": {
    #  "AdverseEffect": [
    #    "Eye allergy"
    #  ],
    #  "AdverseEffectStart": "2017-07-18",
    #  "Dissease": "headake",
    #  "Dose": "mg",
    #  "Medicine": "Aspirin",
    #  "OtherMeds": "only aspirin",
    #  "Remarks": "all",
    #  "StartTime": "10:00:00"

    request = service.spreadsheets().values().append(spreadsheetId=SHEETID, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=values)
    response = request.execute()
    
    return response

def getLines(rowid):

    f = open('conv.txt', 'r')

    i = 1

    result = ""

    for line in f:
        if (i == rowid):
            result = line[:-1]
        i += 1

    return result


def getRows(sheetRange):
    print("Get ROWs" + sheetRange)

    service = gmailLogin()

    # The A1 notation of a range to search for a logical table of data.
    # Values will be appended after the last row of the table.
    range_ = sheetRange  # TODO: Update placeholder value.


    # How values should be represented in the output.
    # The default render option is ValueRenderOption.FORMATTED_VALUE.
    value_render_option = 'UNFORMATTED_VALUE'  # TODO: Update placeholder value.

    # How dates, times, and durations should be represented in the output.
    # This is ignored if value_render_option is
    # FORMATTED_VALUE.
    # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
    #date_time_render_option = ''  # TODO: Update placeholder value.

    request = service.spreadsheets().values().get(spreadsheetId=SHEETID, range=range_, valueRenderOption=value_render_option) #, dateTimeRenderOption=date_time_render_option)
    response = request.execute()
    
    if ('values' in response):
        return response.get("values")[0][0] + " " + response.get("values")[0][1]
    else:
        return ""

#################################################################################################
#################################################################################################
#################################################################################################

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
 
def setSession():
    # Tutaj zrobi sobie pytanie do SAPa
    
    cj = http.cookiejar.CookieJar()
    #opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    #r = opener.open("http://example.com/")
    
    #passwordManager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    #passwordManager.add_password(None, url, userName, passWord);

    #auth_handler = urllib.request.HTTPBasicAuthHandler(passwordManager)

    #opener = urllib.request.build_opener(auth_handler, urllib.request.HTTPCookieProcessor(cj))
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    urllib.request.install_opener(opener)
    return opener
    
def getResultParam(req, field):

    return req.get("result").get("parameters").get(field)

def getLicense(req):
    
    opener = sapLogin()
    
    result = askSap(opener, data=None)

    return result.read().decode('utf-8')

def setValue(sessionId, query=None, event=None):

    values = {
            "v"           : "20150910",
            "sessionId"   : sessionId,
            "lang"        : "en"
            }

    if query is not None:
        values["query"] = query
        return values
    
    if event is not None:
        values["event"] = { "name": event }
        return values

    return None


def postForm(opener, values):
    print("POST FORM")
    
    #    curl -H "Content-Type: application/json; charset=utf-8" -H "Authorization: Bearer YOUR_ACCESS_TOKEN" --data "{'query':'and for tomorrow', 'timezone':'GMT-5', 'lang':'en', 'contexts':[{ 'name': 'weather', 'parameters':{'city': 'London'}, 'lifespan': 4}], 'sessionId':'1234567890'}" "https://api.api.ai/v1/query?v=20150910"
   
    #data = str.encode(urllib.parse.urlencode(values), 'utf-8')
    data = str.encode(json.dumps(values), 'utf-8')

    pprint(data)
    headers = {
            'Authorization': 'Bearer 0171fbb8f73e4d77a9bb918fca99ec6d',
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': len(data)
            }

    result = askPage(opener, data=data, headers=headers, method='POST')
    
    return result.read().decode('utf-8')


def askPage(opener, data=None, headers=None, method='GET'):

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

def getTest(req):

    # Ustalamy sesje - logujemy sie
    # Wywolujemy event, a potem linijka po linijce
    # 

    return 0

def defaultIntent(req):
    
    if ("resolvedQuery" not in req.get("result")):
        return returnSpeech("What's up?")

    if (req.get("result").get("resolvedQuery").upper() == "RECAPS"):
        followupevent = {
            "name": "extractEntities_event"
        }

        speech = "Please provide your message"

    else:
        followupevent = {
            "name": "conversation_event"
        }

        speech = "Good morning! I am chatbot for entity recognition."

    return returnSpeech(speech, followUpEvent=followupevent)


Actions = {
    'get.licenses.list': getLicense,
    'getTest': getTest,
    'Display' : defaultIntent,
    'extractEntities_action': createRow,
    'CreateConv' : createBloterConv
}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ')),
    app.run(debug=True, port=port, host='0.0.0.0')
