
import argparse
import datetime
import json
import tempfile
import requests
import yaml

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

pre_check_dict = {}
post_check_dict = {}

def get_variables (central_info,serial):
    s = requests.Session()

    retries = Retry(total=5,
    backoff_factor=1,
    status_forcelist=[ 502, 503, 504 ])

    access_token = central_info['token']['access_token']
    base_url = central_info['base_url']
    api_function_url = base_url + "/configuration/v1/devices/{0}/template_variables".format(serial)
    qheaders = {
      "Content-Type":"application/json",
      "Authorization": "Bearer " + access_token,
    }

    qparams = {
      "device_serial": serial,
    }

    response = s.request("GET", api_function_url, headers=qheaders, params=qparams)
    if "error" in response.json():
      print(response.text)
      exit()
      return "{'ERROR'}"
    else:
      new_variable_dict = {}
    new_variable_dict[serial] = response.json()['data']['variables']
    return new_variable_dict