import json
import requests
from pprint import pprint

def test_central (central_info_func):
    '''Test token to see if it is valid - if not refresh it'''
    base_url = central_info_func['base_url']
    access_token = central_info_func['token']['access_token']
    refresh_token = central_info_func['refresh_token']['refresh_token']
    oath2_url = base_url + "/oauth2/token"
    api_test_url = base_url + "/monitoring/v1/gateways"
    qheaders = {
        "Content-Type":"application/json",
        "Authorization": "Bearer " + access_token,
        "limit": "1"
    }
    qparams = {
        "limit": 1,
        "offset": 0    
    }
    print("Validating ACCESS TOKEN")
    response = requests.request("GET", api_test_url, headers=qheaders, params=qparams)
    #print(response.text.encode('utf8'))
    #print(response.request.headers)

    if "error" in response.json():
        print("ACCESS TOKEN is INVALID or EXPIRED.  Refreshing tokens...")
        #refresh the token
        qparams = {
            "grant_type":"refresh_token",
            "client_id": central_info_func['client_id'],
            "client_secret": central_info_func['client_secret'],
            "refresh_token": refresh_token
        }
        response = requests.request("POST", oath2_url, params=qparams)
        #print(response.text.encode('utf8'))
        if "error" in response.json():
            print("UNABLE to refresh ACCESS TOKEN. REFRESH TOKEN, CLIENT ID or CLIENT SECRET INVALID - EXITING")
            exit()
        else:
            # extract the new refresh token from the response
            #pprint(central_info_func)
            #pprint(response.json())
            response_payload = response.json()
            refresh_token_new = response_payload['refresh_token']
            access_token_new = response_payload ['access_token']
            central_info_func['token']['access_token'] = access_token_new
            central_info_func['refresh_token']['refresh_token'] = refresh_token_new
            expires_in = response.json()['expires_in']
            central_info_func['expires_in'] = expires_in
            #pprint(central_info_func)
    else:
        print("ACCESS TOKEN is valid.  No action required.")
    return central_info_func