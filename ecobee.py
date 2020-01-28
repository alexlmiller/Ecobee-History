# Update the Settings File
import json
import requests
import urllib

def initialize_settings(api_key):
    settings={'thermostats':{},'tokens':{'api_key':api_key}}
    pretty_settings = json.dumps(settings,indent=4)
    settingsfile = open('settings.json', 'w')
    settingsfile.write(pretty_settings)
    settingsfile.close()

def read_settings(b):
    settingsfile = open('settings.json', 'r')
    settings = json.loads(settingsfile.read())
    settingsfile.close()
    return settings[b]

def write_settings(name,dict):
    settingsfile = open('settings.json', 'r')
    settings = json.loads(settingsfile.read())
    settingsfile.close()
    settings.update({name:dict})
    pretty_settings = json.dumps(settings,indent=4)
    settingsfile = open('settings.json', 'w')
    settingsfile.write(pretty_settings)
    settingsfile.close()

def refresh_tokens():
    tokens=read_settings('tokens')
    authurl = 'https://api.ecobee.com/token'
    authrequest = requests.post(
        authurl,
        params={
            "grant_type":"refresh_token",
            "client_id":tokens["api_key"],
            "code":tokens['refresh_token']
            },
        headers={
            "Content-Type":"application/json;charset=UTF-8"
            }
        )

    if authrequest.status_code == 200:
        print ('Token Refresh Sucessful, Continuing...')
        tokens.update({"access_token": authrequest.json()['access_token'], "refresh_token": authrequest.json()['refresh_token']})
        print('New Access Token: ' + tokens['access_token'])
        print('New Refresh Token: ' + tokens['refresh_token'])
        write_settings('tokens',tokens)
        return tokens

    else:
        print (authrequest.status_code)
        print (authrequest.headers)
        print (authrequest.json)

def get_thermostats():
    thermostats=read_settings('thermostats')
    tokens=read_settings('tokens')
    # Build The Reporting Request

    loadbody = {
        "selection": {
            "selectionType": "registered",
            "selectionMatch": ""
            }
        }
    jsonbody = urllib.parse.quote_plus(json.dumps(loadbody))

    # Get Data From Ecobee
    url = 'https://api.ecobee.com/1/thermostat'
    request = requests.get(
        url,
        params={
            "json":jsonbody
            },
        headers={
            "Content-Type":"application/json;charset=UTF-8",
            "Authorization": 'Bearer ' + tokens['access_token']
            }
        )

    if request.status_code == 200:
        print ('Thermostat Fetch Sucessful, Continuing...')
        thermostatjson = request.json()['thermostatList']
        thermostats={}
        for thermostat in thermostatjson:
            thermostats.update({thermostat['name'] : thermostat['identifier']})
        print('Here are your Thermostats: ' + json.dumps(thermostats,indent=4))
        write_settings('thermostats',thermostats)
        return thermostats

    else:
        print (request.status_code)
        print (request.headers)
        print (request.json)
