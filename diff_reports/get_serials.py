import json
import requests
from pprint import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from validate_central import test_central

def get_serials_swarm_leader(central_info,site):
    """ Get IAP Serials for Site """
    return

def get_serials_site(central_info,site):
    """ Get CX Serials for Site """
    switch_dict = {}
    print ("Getting serials for "+site)
    name = site
     
    s = requests.Session()
    retries = Retry(total=5,
    backoff_factor=2,
    status_forcelist=[ 502, 503, 504 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))
 
    access_token = central_info['token']['access_token']
    base_url = central_info['base_url']
    api_function_url = base_url + '/monitoring/v1/switches'
    qheaders = {
      "Content-Type":"application/json",
      "Authorization": "Bearer " + access_token,
    }

    qparams = {
      "site": name
    }

    response = s.request("GET", api_function_url, headers=qheaders, params=qparams)
    # get new token if token is expired and try again
    if (response.status_code == 401):
        central_info = test_central(central_info)
        response = s.request("GET", api_function_url, headers=qheaders, params=qparams)
        response_payload=(response.json())

    # if response is 200 all is good 
    elif (response.status_code == 200):
        response_payload=(response.json())

    # if response is something else return
    else:
        pprint(response.json())
        return switch_dict,central_info

    stacks=[]
    for item in response_payload['switches']:
        if item['stack_id'] == None:
            name = item['name']
            switch_dict[name]={}
            switch_dict[name]['firmware'] = item['firmware_version']
            switch_dict[name]['group'] = item['group_name']
            switch_dict[name]['serial'] = item['serial']
            switch_dict[name]['ip_address'] = item['ip_address']
            switch_dict[name]['status'] = item['status']
        else:
            stack = item['stack_id']
            if stack not in stacks:
                stacks.append(stack)
            else:
                pass
    if stacks != '':
        for stack in stacks:
            api_function_url2 = base_url + '/monitoring/v1/switch_stacks/'+stack
            print("Getting Stack Info")
            response2 = s.request ("GET", api_function_url2, headers=qheaders)
            if (response2.status_code == 401):
                central_info = test_central(central_info)
                response2 = s.request("GET", api_function_url2, headers=qheaders)
                response2_payload=(response2.json())
            # if response is 200 all is good 
            elif (response2.status_code == 200):
                response2_payload=(response2.json())
            # if response is something else return
            else:
                pprint(response2.json())
                return switch_dict,central_info
            name = response2_payload['name']
            commander_mac = response2_payload['mac']
            switch_dict[name]={}
            switch_dict[name]['group']=response2_payload['group']
            switch_dict[name]['commander_mac']=commander_mac
            switch_dict[name]['firmware']=[]
            for item in response_payload['switches']:
                if item['name'] == name:
                    switch_dict[name]['firmware'].append(item['firmware_version'])
                    if item['macaddr'] == commander_mac:
                        switch_dict[name]['serial']=item['serial']
                        switch_dict[name]['ip_address']=item['ip_address']
                        switch_dict[name]['status'] = item['status']
                    else:
                        pass
                else:
                    pass
    return switch_dict,central_info