import requests
import json
import urllib
import csv
import time
import datetime
from datetime import timedelta
from ecobee import *

# Get Current Settings & Store
thermostats=read_settings('thermostats')
tokens=read_settings('tokens')
api_key = tokens['api_key']

# Setup the User Input Request
thermostatstring=""
for key in thermostats.keys(): thermostatstring+=str(key + '\n')
therm_text = 'Which Thermostat Are You Looking At?\n{}: '.format(thermostatstring)

# Capture Inputs for Reporting
start = input('Start Date? (YYYY-MM-DD): ')
end = input('End Date? (YYYY-MM-DD): ')
thermostat = input(therm_text)
started = datetime.datetime.strptime(start, "%Y-%m-%d")
ended = datetime.datetime.strptime(end, "%Y-%m-%d")

# Refresh Tokens
tokens = refresh_tokens()

# Open the CSV
csvname = 'Ecobee Data - {} - {} to {}.csv'.format(thermostat,start,end)
reportcsv = open(csvname, 'w')
csvwriter = csv.writer(reportcsv, delimiter=',')
header = ['date','time','temp','humidity']
csvwriter.writerow(header)

# Figure Out The Timing
startdate = started
enddate = min(ended, startdate + timedelta(days=15))

while enddate <= ended:
    # Build The Reporting Request
    loadbody = {
        "startDate": str(startdate)[:10],
        "endDate": str(enddate)[:10],
        "columns": "zoneAveTemp,zoneHumidity",
        "selection": {
            "selectionType": "thermostats",
            "selectionMatch": thermostats[thermostat]
            }
        }
    jsonbody = urllib.parse.quote_plus(json.dumps(loadbody))

    # Get Data From Ecobee
    url = 'https://api.ecobee.com/1/runtimeReport'
    request = requests.get(
        url,
        params={
            "format":"json",
            "json":jsonbody
            },
        headers={
            "Content-Type":"application/json;charset=UTF-8",
            "Authorization": 'Bearer ' + tokens['access_token']
            }
        )

    # If the request is successful, write the CSV file
    if request.status_code == 200:
        print (str(startdate) + ' to ' + str(enddate) + ' Complete, Continuing...')
        report = request.json()['reportList']
        reportdata = report[0]['rowList']
        reportjson = json.dumps(reportdata)
        reportdict = json.loads(reportjson)

        for datapoint in reportdict:
            datas = datapoint.split(',')
            csvwriter.writerow(datas)

    # If it Fails Tell Me Why
    else:
        print (request.status_code)
        print (request.headers)
        print (request.json())

    print ('adjusting dates...')
    startdate = enddate + timedelta(days=1)
    print ('new start: ' + str(startdate)[:10])
    enddate = min(ended, startdate + timedelta(days=15))
    print ('new end: ' + str(enddate)[:10])

    if startdate > enddate:
        break
    time.sleep(2)

reportcsv.close()
