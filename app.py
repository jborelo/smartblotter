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

from concurrent.futures import ProcessPoolExecutor

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
SourceSheetID = '179hCtu13Divv0vMU5J0M-j6clcS9meMmPRyJ9te92xA'
DestSheetID = '1loP91vw5QiQSXLeDePXddbQKO0xFIN3bzyamiE0AaJ0'

sapurl = 'http://80.241.97.49:50000/sap/opu/odata/LMC/OLI_MOBILE_SRV/CZAT_TEST_SET'
userName = 'AISAP_TEST'
passWord = 'asyai.1'

# WARNING - Queue is created by file, every new record needs \n - end of line
siteUpdate = {
    "location": {
                "default": { 
                                'graph': '<img class="img-fluid " src="production/images/MahulContent/Gas_UK_NBP_grey.png" alt="" style="height: 27em">\n',
                                'table': '<img class="img-fluid " src="production/images/MahulContent/tblGas-UK-NBP.png" alt="" >\n',
                                'news': '<ul class="middlebar_nav p-3"><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/flag_ico.png" alt=""></a> <b class="blue">UK Gas Market Rallies on the back of the Oil market</b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/ship_ico.png" alt=""></a> <b class="blue"> Spark spreads narrow as gas market tightens </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/hands_ico.png" alt=""></a> <b class="blue"> Norway supplies to UK slip </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/city_ico.png" alt=""></a> <b class="blue"> NBP holding up despite falling power prices </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li></ul>\n'
                            },
                "dutch": { 
                                'graph': '<img class="img-fluid " src="production/images/MahulContent/Gas_Netherlands_TTF_grey.png" alt="" style="height: 27em">\n',
                                'table': '<img class="img-fluid " src="production/images/MahulContent/tblGas-Netherlands-TTF.png" alt="" >\n',
                                'news': '<ul class="middlebar_nav p-3"><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/NL/comp_ico.png" alt=""></a> <b class="blue"> Netherlands might be net importer within 3 years, says report </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/NL/yard_ico.png" alt=""></a> <b class="blue"> TTF prices holding firm </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/NL/tunel_ico.png" alt=""></a> <b class="blue"> Dutch trading volumes strong </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/NL/water_ico.png" alt=""></a> <b class="blue"> Market Moves: TTF Curve Rises </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li></ul>\n'
                             },
                "german": { 
                                'graph': '<img class="img-fluid " src="production/images/MahulContent/Gas_Germany_Gaspool_grey.png" alt="" style="height: 27em">\n',
                                'table': '<img class="img-fluid " src="production/images/MahulContent/tblGas-Germany-Gaspool.png" alt="" >\n',
                                'news': '<ul class="middlebar_nav p-3"><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/GER/euro_ico.png" alt=""></a> <b class="blue"> Record trading on PEGAS futures platform </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/GER/index_ico.png " alt=""></a> <b class="blue"> German Gas Market Rallies on strong demand </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src=" production/images/ico/GER/man_ico.png " alt=""></a> <b class="blue"> PEGAS announces new index </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src=" production/images/ico/GER/report_ico.png " alt=""></a> <b class="blue"> Dutch, German spot natural gas prices hold onto gains despite supply concerns </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li></ul>\n'
                             },
                "ncg": { 
                                'graph': '<img class="img-fluid " src="production/images/MahulContent/Gas_Germany_NCG_grey.png" alt="" style="height: 27em">\n',
                                'table': '<img class="img-fluid " src="production/images/MahulContent/tblGas-Germany-NCG.png" alt="" >\n',
                                'news': '<ul class="middlebar_nav p-3"><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/GER/euro_ico.png" alt=""></a> <b class="blue"> Record trading on PEGAS futures platform </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/GER/index_ico.png " alt=""></a> <b class="blue"> German Gas Market Rallies on strong demand </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src=" production/images/ico/GER/man_ico.png " alt=""></a> <b class="blue"> PEGAS announces new index </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src=" production/images/ico/GER/report_ico.png " alt=""></a> <b class="blue"> Dutch, German spot natural gas prices hold onto gains despite supply concerns </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li></ul>\n'
                             },
                "gb": { 
                                'graph': '<img class="img-fluid " src="production/images/MahulContent/Electricity_Power_UK_grey.png" alt="" style="height: 27em">\n',
                                'table': '<img class="img-fluid " src="production/images/MahulContent/tblUK-Electricity-Baseload-GRG.png" >\n',
                                'news': '<ul class="middlebar_nav p-3"><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/flag_ico.png" alt=""></a> <b class="blue">UK Gas Market Rallies on the back of the Oil market</b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/ship_ico.png" alt=""></a> <b class="blue"> Spark spreads narrow as gas market tightens </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/hands_ico.png" alt=""></a> <b class="blue"> Norway supplies to UK slip </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/UK/city_ico.png" alt=""></a> <b class="blue"> NBP holding up despite falling power prices </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li></ul>\n'
                             },
                "crude": { 
                                'graph': '<img class="img-fluid " src="production/images/MahulContent/Crude_Oil_Brent_grey.png" alt="" style="height: 27em">\n',
                                'table': '<img class="img-fluid " src="production/images/MahulContent/tblCrude-Brent.png" alt="" >\n',
                                'news': '<ul class="middlebar_nav p-3"><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/OIL/paper_ico.png" alt=""></a> <b class="blue"> Oil Market Tighter After Hurricane Harvey </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/OIL/fuel_ico.png" alt=""></a> <b class="blue"> Traders Expect Much Tighter Oil Markets In Early 2018</b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/OIL/change_ico.png" alt=""></a> <b class="blue"> Crude oil market likely to turn choppy </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li><li><a class="mbar_thubnail" href="#"><img class="pt-3"src="production/images/ico/OIL/strike_ico.png" alt=""></a> <b class="blue"> Oil ends higher as market assesses Irma’s demand impact </b> <br/> <small>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Lorem ipsum dolor sit amet, consectetur adipisicing elit...</small></li></ul>\n'
                             },
            }
        }

 

keywordsMapping = {
    "uk gas": "default",
    "nbp": "default",
    "dutch gas": "dutch",
    "netherlands gas": "dutch",
    "ttf": "dutch",
    "german": "german",
    "german gas": "german",
    "gaspool": "german",
    "ncg": "ncg",
    "net connect": "ncg",
    "uk electricity": "gb",
    "uk power": "gb",
    "gb electricity": "gb",
    "gb power": "gb",
    "british power": "gb",
    "crude oil": "crude",
    "crude": "crude",
    "oil markets": "crude",
    "power in uk": "gb",
        }

userNames = {
        "U51AG5P50": "Cyrus",
        "U50KLKUQL": "Mahul" 
        }


#--------------------------------------------------------------
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


#--------------------------------------------------------------
@app.route('/querytext', methods=['POST'])
def queryText():
    req = request.get_json(silent=True, force=True)

    print("Querytext:")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    qdir = os.path.join(script_dir, "A6XMCTM7A", "T4ZSTBWU8", "PY65kzYVuPSsilmUlpmWz0tF")

    try: 
        for key in os.listdir(qdir):
            print(key)
            qfile = os.path.join(qdir, key)
            print("###FILE")
            f = open(qfile, 'r')
            for line in f:
                print(line)
    except IOError as e:
        print(e)
 
    res = { "text": "OK" }
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


#-------------  piszemy dl slacka (NOT USED !!)----------------
@app.route('/sayToSlack', methods=['POST'])
def sayToSlack():
    req = request.get_json(silent=True, force=True)

    print("sayToSlack:")
    print(json.dumps(req, indent=4))

    res = { "text": "OK" }
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


#-------------- Slack wysyla eventy tutaj -------------
@app.route('/slackevents', methods=['POST'])
def slackEvents():
    req = request.get_json(silent=True, force=True)


# event od slacka idzie do  kolejek (plikow) i zwracamy 200
#  tak naprawde zalozone jest ze res sie skonczy i jego wynik 
#  do sprawdzenia
# startowany jest proces (thread)  do  rozmowy z APi.AI


    executor = ProcessPoolExecutor(5)
    print("--------------- SlackEvent:")
    print(json.dumps(req, indent=4))

    if ("challenge" in req):
        res = slackverify(req)
    else:
        res = executor.submit(slacksafe, req) # slacksafe() saves text got from slack to local file 'slack'
        res2 = executor.submit(apiaiAsk, req) # apiaiAsk sie wykonuje w tle  dluzej i rozmawia z API.AI
        executor.shutdown(wait=False)
        return res.result()
        
    return res


#------------------------------------------------------------
@app.route('/copyConfirm', methods=['GET'])
def copyConfirm():
    
    result = getRows(SourceSheetID, "Trades to confirm!A5:L")

    #print(result)
    i = 4
    for row in result:
        i += 1
        if len(row) > 11 and row[11] == "Confirmed":
            sheetRange = "Trades to Confirm!L" + str(i)
            value = { "values": [ [ "Submitted" ] ] }

            updateRow(SourceSheetID, sheetRange, value)
            print(sheetRange)
            print(row)
            valueAdd = { "values": [ row ] }
            appendRow("", DestSheetID, "Deal List!A2", valueAdd)

    return jsonify(result="Copied")


# ------ called by index.html to return events -----
@app.route('/getEvents', methods=['GET'])
def getEvents():
    print("-- getEventssss  ---")
#    resLen = 200

    result = {}
    rowsid = {}

    rowid = 1
    try: 
        script_dir = os.path.dirname(os.path.realpath(__file__))
        qdir = os.path.join(script_dir, "A6XMCTM7A", "T4ZSTBWU8", "PY65kzYVuPSsilmUlpmWz0tF")

        for key in os.listdir(qdir): 
            #print(key)
            if key in request.cookies:
                rowid = int(request.cookies.get(key))
            else:
                rowid = 1

            oneresult, rowid = getLines(key, rowid)

            if len(oneresult) > 3:
                result[key] = { "result": oneresult, "status": "New" }
            else:
                result[key] = { "result": "", "status": "Old" }
            rowsid[key] = rowid
    except IOError as e:
        #print(e)
        result = {"OK": "OK"}
    
    result = json.dumps(result, indent=4)
    #print(result)
    response = make_response(result)
    for key in rowsid:
        response.set_cookie(key, value=str(rowsid[key]), max_age=25)
    return response


#------------------------------------------
@app.route('/<path:path>')
def root(path):
    print("Path: " + path)   
    # print(os.path.dirname(os.path.realpath(__file__)))

    return app.send_static_file(path)


#------------------------------------------
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


#----------  stores text from request to file 'slack' in order to show in web  --------------------------------
def slacksafe(req):
    # SlackEvent:
    # {
    #     "token": "PY65kzYVuPSsilmUlpmWz0tF",
    #     "team_id": "T4ZSTBWU8",
    #     "api_app_id": "A6XMCTM7A",
    #     "event": {
    #         "text": "Co niby super",
    #         "bot_id": "B6XTMJCDP",
    #         "type": "message",
    #         "subtype": "bot_message",
    #         "ts": "1504890432.000434",
    #         "channel": "C6Z7QKR8E",
    #         "event_ts": "1504890432.000434"
    #     },
    #     "type": "event_callback",
    #     "authed_users": [
    #         "U51AG5P50"
    #     ],
    #     "event_id": "Ev70ENM5MK",
    #     "event_time": 1504890432
    # }
    print("-- in slacksave() --")
    #time.sleep(5)
    qdir = setupDirs(req)
    qfile = os.path.join(qdir, 'slack')

    # print(qfile)

    slackMessage = getSlackUsername(req) + "</br>" + req.get("event").get("text").replace('\n', '</br>') + "\n"
    #print(slackMessage)

    with open(qfile, "a") as myfile:
        myfile.write(slackMessage)
    
    print("Dodane do pliku slack: " + slackMessage)
    res = { "result": "OK" }
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    r.headers['X-Slack-No-Retry'] = 1

    return r


#-------------------------------------------------------------------------------------------------
def setupDirs(req):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    #qdir = os.path.join(script_dir, req.get("api_app_id"), req.get("team_id"), req.get("token"))
    qdir = os.path.join(script_dir, "A6XMCTM7A", "T4ZSTBWU8", "PY65kzYVuPSsilmUlpmWz0tF")

    if (not os.path.isdir(qdir)):
        os.makedirs(qdir, mode=0o777, exist_ok=True)

    return qdir


#------------------------------------------
def getApiaiSessionID(req, opener):
    print("-- in getApiaiSessionID() --")

    url = "https://api.api.ai/v1/contexts?sessionId=" + req.get("token")
    result = askPage(opener, url=url, headers=setHeaders())

    result = result.read().decode('utf-8')

    #print(result)
    #print(len(result))
    if (result is not None and len(result) > 5):
        return result

    return None


#----------------------------------------------------
def setApiaiSessionID(req, opener):
    print("-- in setApiaiSessionID() --")

    url = "https://api.api.ai/v1/contexts?sessionId=" + req.get("token")
    result = askPage(opener, url=url, headers=setHeaders(), method='DELETE')
    
    event = {
            "name": "conversation_event",
            "data": {
                "recaps":"recaps"
                }
            }

    postForm(opener, setValue(req.get("token"), event=event))

    return getApiaiSessionID(req, opener)


#-------------------------------------------------------------
def postApiAI(opener, req):
    print("-- in postApAI() --")
    maxloops = 10
    i = 0
    while(True):
        print("")
        print ("loop: " + str(i))
        result = postForm(opener, setValue(req.get("token"), query=req.get("event").get("text")))
        result = json.loads(result)
        i += 1
        rescode = result.get("status").get("code") 
        print(result)

        if(rescode == 200):
            print("APIAI returned 200")
            break

        if ( i > maxloops):
            print ("Maxloops exceded!")
            break

         
    print("Finish postAPIAIi with rescode: " + str(rescode))
    return result


# ---------- talks in separate process (currently not thread) with  API.AI to parse  submition  ------------------
def apiaiAsk(req): 
    print("--in apiaiAsk() --")
    opener = setSession()
    sessionID = getApiaiSessionID(req, opener)

    if ("recap" in str.lower(req.get("event").get("text"))):
        print("RECUP found")
        sessionID = setApiaiSessionID(req, opener)
    elif ("user" not in req.get("event")):
        print("BOT GADA")
        return True
   
    grepSpeech(req)
    # We are waiting for RECAPS"
    
    if (sessionID is None):
        print("apiaiAsk Break")
        return True

    print("RECAPS")
    # TODO Setup sessionID
    apiai = postApiAI(opener, req) 
    print("Result APIAI:")
    print(apiai)
    #print(type(apiai))
    #print(type(apiai))
    #manageApiResult(req, apiai)
    if ("recap" in str.lower(req.get("event").get("text")) and len(req.get("event").get("text")) < 15):
        print("Ignore botAdvice")
        talkToSlack("ok, please do it")
        return True    
    botAdvices(apiai, req)
    return True


# ------    wysylanie REST do SLACKA  --------
def talkToSlack(speech):
    print("Talk to Slack")
    #url = "https://hooks.slack.com/services/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"
    #url  = "https://hooks.slack.com/services/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"
    url = "https://hooks.slack.com/services/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"  # incoming Slack webhookk
    
    text = { "text": speech }
    data = json.dumps(text).encode('utf8')
    request = urllib.request.Request(url, data=data, headers={'content-type': 'application/json'})

    response = urllib.request.urlopen(request)
    return ""


#------------------------------------------------------------------------------------------------------
def botAdvices(req, slackreq):
    print("-- in botAdvices() --")
    print(req)
    if (getParam(req, "recaps") == "recaps" and req.get("result").get("actionIncomplete") == True):
        talkToSlack(req.get("result").get("fulfillment").get("speech"))

    if req.get("result").get("actionIncomplete") == False:
        createRow(req)
        talkToSlack("Got it, thank you")

    return ""


#-------------------------------------------------------------------------------------
def getSlackUsername(req):
    # TODO decode SlackUserID to real Username
    if ("user" in req.get("event")):
        if (req.get("event").get("user") in userNames):
            result = userNames.get(req.get("event").get("user"))
        else:
            result =  req.get("event").get("user")
    else:
        result = "BOT"
        
    return "<b>" + result + "</b>"


#-------------------------------------------------------------------
def slackverify(req):
    print("SlackVerify")
    result = { "challenge" : req.get("challenge") }
    res = json.dumps(result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    r.headers['X-Slack-No-Retry'] = 1

 
    #print(result)
    return r


#-------------------------------------------------------------------
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


#--------------------------------------------------------------------------------------
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

#-------------------------------------------------------------------
def getParam(req, field):
    if (field in req.get("result").get("parameters")):
        if (type(req.get("result").get("parameters").get(field)) is list):
            return ", ".join(str(req.get("result").get("parameters").get(field)))
        else:
            return str(req.get("result").get("parameters").get(field))
    return None

#-------------------------------------------------------------------
def getSParam(req, field):
    result = getParam(req, field)
    if result is None:
        return ""

    return result

#-------------------------------------------------------------------
def grepSpeech(req):
    for word in keywordsMapping:
        if (word in str.lower(req.get("event").get("text"))):
            print("grepSpeech")
            field = keywordsMapping.get(word)
            eventSave(req, "location", field)
            break

    return None

#-------------------------------------------------------------------
def manageApiResult(req, apiai):
    query = apiai.get("result").get("resolvedQuery")
    print("manageApiResult")
    print(query)
    for context in apiai.get("result").get("contexts"):
        print(context)
        print(type(context.get("parameters")))
        for key in context.get("parameters"):
            if (query in context.get("parameters").get(key)):
                #TODO update html on page
                field = key.split(".")[0]
                eventSave(req, field, getParam(apiai, field))
                return "OK"
                
    return None


#-------------------------------------------------------------------
def eventSave(req, field, value):
    print("event: %s, %s" % (field, value))
    if (field in siteUpdate):
        content = siteUpdate.get(field).get(value)
        for key in content:
            qfile = os.path.join(setupDirs(req), key)
            print(qfile)
            with open(qfile, "a") as myfile:
                myfile.write(content.get(key))

    return ""


#-------------------------------------------------------------------
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

#-------------------------------------------------------------------
def getStrFromDict(value):
    result = ""
    for key in value:
        result += "%s " % value[key]

    return result

#-------------------------------------------------------------------
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


#-------------------------------------------------------------------
def prepareHeaders(req):
    print("Create Headers")
    value_range_body = {
        "values": [
            [ 
                "Deal #", "Deal Date", "Buyer", "Seller", "StartDate", "EndDate", "Quantity", "QuantityUnit", "Price", "Currency", "Location"
            ]
        ]

    }

    appendRow(req, SourceSheetID, "Trades to confirm!A4", value_range_body)

    speech = "Headers are created"

    return returnSpeech(speech)

#-------------------------------------------------------------------
def createBloterConv(req):

    if req.get("result").get("actionIncomplete") == True:
        return returnSpeech(req.get("result").get("fulfillment").get("speech"))

    return createRow(req)

#-------------------------------------------------------------------
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

#-------------------------------------------------------------------
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

#-------------------------------------------------------------------
def getDateArray(oneArray):
    dateArray = []
    testDate = None

    for one in oneArray:
        testDate = one.split('/')
        for second in testDate:
            dateArray.append(datetime.datetime.strptime(second, '%Y-%m-%d'))
    
    return dateArray

#-------------------------------------------------------------------
def getMaxNumber(req, field):
    testOne = None

    for one in req.get("result").get("parameters").get(field):
        if (testOne is None) or testOne < one:
            testOne = one

    if testOne is None:
        return ""
    else:
        return testOne

#-------------------------------------------------------------------
def getMinNumber(req, field):
    testOne = None

    for one in req.get("result").get("parameters").get(field):
        if (testOne is None) or testOne > one:
            testOne = one

    if testOne is None:
        return ""
    else:
        return testOne


#-------------------------------------------------------------------
def createRow(req):
    print("-- in createROW --")

    #createConv(req)
    if ("resolvedQuery" in req.get("result") and (req.get("result").get("resolvedQuery") == "HI" or req.get("result").get("resolvedQuery") == "conversation_event")):
        print("seems Normal Conversation")
        return returnSpeech("NORMAL CONVERSATION")

    if ("resolvedQuery" in req.get("result") and (req.get("result").get("resolvedQuery") == "RECAPS" or req.get("result").get("resolvedQuery") == "extractEntities_event")):
        print("seems getting recaps")
        return returnSpeech("Get RECAPS")


    print("entities detect mode")


    #if req.get("result").get("actionIncomplete") == True:
    #    return returnSpeech(req.get("result").get("fulfillment").get("speech"))

    dealNr = "%f" % time.time()

    print("entities detect mode 2")
    value_range_body = {
        "values": [
            [ 
                dealNr[:10],                                    # Deal Number
                datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y'), # Current Date
                print("buyer"),        # Buyer
                getSParam(req, "buyer"),        # Buyer
                print("trader"),        # Buyer
                getSParam(req, "trader"),       # Seller
                print("min date-per"),        # Buyer
                #getMinDate(req, "date-period"),    # StartDate jbo
                "2018-01-01",
                print("max date-per"),        # Buyer
                #getMaxDate(req, "date-period"),    # EndDate
                "2018-01-01",
                print("quan"),        # Buyer
                getSParam(req, "quantity"),     # Quantity #getMaxNumber(req, "number1"),     # Quantity
                print("quan unit"),        # Buyer
                getSParam(req, "quantityunit"), # QuantityUnit
                print("price"),        # Buyer
                getSParam(req, "price"),        # Price #getMinNumber(req, "number1"),        # Price
                print("curren"),        # Buyer
                getSParam(req, "currency"),     # Currency
                #"GBP",                          # Currency
                print("location"),        # Buyer
                getSParam(req, "locatio")      # Location
            ]
        ]

    }

    print(" ** entities detect mode 3")
    print(value_range_body)
    appendRow(SourceSheetID, "Trades to confirm!A5", value_range_body)

    speech = "Added"

    #return returnSpeech(req.get("result").get("fulfillment").get("speech"))
    return returnSpeech(speech)



#-------------------------------------------------------------------
def createConv(req):
    
    client = "Client: " + req.get("result").get("resolvedQuery") + "\n"
    bot = "Bot: " + req.get("result").get("fulfillment").get("speech") + "\n"
    
    with open("conv.txt", "a") as myfile:
        myfile.write(client)
        myfile.write(bot)

    return returnSpeech(req.get("result").get("fulfillment").get("speech"))


#-------------------------------------------------------------------
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

    appendRow(SourceSheetID, "Arkusz2!A1", value_range_body)

    return returnSpeech(req.get("result").get("fulfillment").get("speech"))


#-------------------------------------------------------------------
def appendRow(sheetid, sheetRange, values):
    print("-- in appnedRow()")

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

    request = service.spreadsheets().values().append(spreadsheetId=sheetid, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=values)
    response = request.execute()
    
    return response


#-------------------------------------------------------------------
def updateRow(sheetid, sheetRange, values):
    print("Update ROW")

    service = gmailLogin()

    # The A1 notation of a range to search for a logical table of data.
    # Values will be appended after the last row of the table.
    range_ = sheetRange  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'RAW'  # TODO: Update placeholder value.

    # How the input data should be inserted.
    #insert_data_option = 'INSERT_ROWS'  # TODO: Update placeholder value.

    #request = service.spreadsheets().values().append(spreadsheetId=sheetid, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=values)
    #response = request.execute()
    request = service.spreadsheets().values().update(spreadsheetId=sheetid, range=range_, valueInputOption=value_input_option, body=values)
    response = request.execute()
 
    return response


#-------------------------------
def getLines(filename, rowid):
    #"token": "PY65kzYVuPSsilmUlpmWz0tF",
    #"team_id": "T4ZSTBWU8",
    #"api_app_id": "A6XMCTM7A",
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    qdir = os.path.join(script_dir, "A6XMCTM7A", "T4ZSTBWU8", "PY65kzYVuPSsilmUlpmWz0tF", filename)
    #                               "api_app_id", req.get("team_id"), req.get("token")

    #print(qdir)

    try:
        f = open(qdir, 'r')
    except IOError as e:
        print("in getLines(), can not open file: " + qdir)
        return "", 0

    i = 1
    result = ""

    for line in f:
        if (i >= rowid):
            result += line # [:-1] 
            result += "</br>"
        
        #print("%d. %s" % (i, result))
        i += 1

    #print("%d. %s" % (i, result))

    return result, i


#-------------------------------------------------------------------
def getRows(sheetid, sheetRange):
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

    request = service.spreadsheets().values().get(spreadsheetId=sheetid, range=range_, valueRenderOption=value_render_option) #, dateTimeRenderOption=date_time_render_option)
    response = request.execute()
    
    if ('values' in response):
        return response.get("values")
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
 

#------------------------------------------------------------------------------------
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


#-------------------------------------------------
def getResultParam(req, field):

    return req.get("result").get("parameters").get(field)

#-------------------------------------------------
def getLicense(req):
    
    opener = sapLogin()
    
    result = askSap(opener, data=None)

    return result.read().decode('utf-8')

#-------------------------------------------------
def setValue(sessionId, query=None, event=None):

    values = {
            "v"           : "20170712",
            "sessionId"   : sessionId,
            "lang"        : "en"
            }

    if query is not None:
        values["query"] = query
        return values
    
    if event is not None:
        values["event"] = event
        return values

    return None

#-------------------------------------------------
def setHeaders():
    headers = {
            'Authorization': 'Bearer f6c6b3478a5e43afb16dcb91b2778d13',
            'Content-Type': 'application/json; charset=utf-8',
            }

    return headers


#-------------------------------------------------
def postForm(opener, values):
    print("POST FORM")
    
    #    curl -H "Content-Type: application/json; charset=utf-8" -H "Authorization: Bearer YOUR_ACCESS_TOKEN" --data "{'query':'and for tomorrow', 'timezone':'GMT-5', 'lang':'en', 'contexts':[{ 'name': 'weather', 'parameters':{'city': 'London'}, 'lifespan': 4}], 'sessionId':'1234567890'}" "https://api.api.ai/v1/query?v=20150910"
   
    #data = str.encode(urllib.parse.urlencode(values), 'utf-8')
    data = str.encode(json.dumps(values), 'utf-8')

    pprint(data)
    headers = setHeaders()
    headers['Content-Length'] = len(data)
    result = askPage(opener, data=data, headers=headers, method='POST')
    
    return result.read().decode('utf-8')


#--------------------------------------------------------------------------------------------------------
#  new: api.dialogflow.com/v1
#--------------------------------------------------------------------------------------------------------
def askPage(opener, url="https://api.api.ai/v1/query?v=20170712", data=None, headers=None, method='GET'):
    print("-- in askPage() --")
    request = urllib.request.Request(url, method=method)
    if headers is not None:
        for key in headers:
            request.add_header(key, headers[key])

    print("method: ")
    pprint(request.get_method())
    print("url: ")
    pprint(request.get_full_url())
    print("items: ")
    pprint(request.header_items())
    print(" ")

    try:
        result = opener.open(request, data)
    except IOError as e:
        print("!!!! ERROR!!!")
        print (e)

    return result


#-----------------------------------------------
def getTest(req):

    # Ustalamy sesje - logujemy sie
    # Wywolujemy event, a potem linijka po linijce
    # 

    return 0


#-----------------------------------------------
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
    'Display' : getTest, # defaultIntent,
    'extractEntities_action': createRow,
    'CreateConv' : createBloterConv
}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 80))

    print("Starting app.py on port %d" % port)
    print(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ')),
    app.run(debug=True, port=port, host='0.0.0.0')
