import requests
import json
from ecobee import *

# Initialize the settings File
api_key='VjQCoYWCIsurPcd2YoaiTwAmCC6wOoXg'
initialize_settings(api_key)

# Set Variables
tokens=read_settings('tokens')
api_key = tokens['api_key']

# Initiate the PIN Process
authurl = 'https://api.ecobee.com/authorize'
authrequest = requests.get(
    authurl,
    params={
        "response_type":"ecobeePin",
        "client_id":api_key,
        "scope":'smartRead'
        },
    headers={
        "Content-Type":"application/json;charset=UTF-8"
        }
    )

# If request is succesful, show the PIN and store the auth code
if authrequest.status_code == 200:
    step1 = authrequest.json()
    print ("\nYour Ecobee PIN is: {}\nPlease Go To Your Ecobee Dashboard and Enter Your PIN\n".format(step1['ecobeePin']))
    tokens.update({"auth_token": step1['code']})
    auth_token = step1['code']
    write_settings('tokens',tokens)
    ready = input('Then Press Enter When Ready To Continue\n')

# If not, tell me why
else:
    print (authrequest.status_code)
    print (authrequest.headers)
    print (authrequest.json())

# Once ready, get the first set of tokens
authurl = 'https://api.ecobee.com/token'
authrequest = requests.post(
    authurl,
    params={
        "grant_type":"ecobeePin",
        "client_id":api_key,
        "code":auth_token
        },
    headers={
        "Content-Type":"application/json;charset=UTF-8"
        }
    )

# If request is succesful, show the PIN and store the auth code
if authrequest.status_code == 200:
    step2 = authrequest.json()
    tokens.update({"access_token": authrequest.json()['access_token'], "refresh_token": authrequest.json()['refresh_token']})
    write_settings('tokens',tokens)
    print ('Your Authorization was successful and your tokens have been stored!')

# If not, tell me why
else:
    print (authrequest.status_code)
    print (authrequest.headers)
    print (authrequest.json())

# Get a list of the thermostats
therms = get_thermostats()
