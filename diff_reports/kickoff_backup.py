import json
import requests
from pprint import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from validate_central import test_central

def kickoff_individual_backup(central_info,device,bu_name):
    """ Kickoff individual device show run """
    print ("kicking off backup for "+device)
     
    s = requests.Session()
    retries = Retry(total=5,
    backoff_factor=1,
    status_forcelist=[ 502, 503, 504 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))
 
    access_token = central_info['token']['access_token']
    base_url = central_info['base_url']
    api_function_url = base_url + '/troubleshooting/v1/running-config-backup/serial/'+device+'/prefix/'+bu_name
    qheaders = {
      "Content-Type":"application/json",
      "Authorization": "Bearer " + access_token,
    }

    response = s.request("POST", api_function_url, headers=qheaders)
    # get new token if token is expired and try again
    if (response.status_code == 401):
        central_info = test_central(central_info)
        response = s.request("POST", api_function_url, headers=qheaders)
        return central_info
    else:
        return central_info