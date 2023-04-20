import json
import requests
import time
import os
import shutil
from jinja2 import Environment, FileSystemLoader
from time import gmtime, strftime
from pprint import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from validate_central import test_central

def write_out_config (serialnum,config_type,config_info,tstamp,ticket,pre_post_type,name,site,site_dict):
    """Template out config files"""
    print('Write Config: '+name)
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('running_output.j2')
    device_serial=serialnum
    file_name=config_type+'.txt'
    directory = 'change_data/'+ticket+'/'+name+'/'+pre_post_type
    file_full_path = directory+'/'+file_name
    archive_directory = 'change_data/'+ticket+'/'+name+'/'+pre_post_type+'/archive'
    dir_exists = os.path.exists(directory)
    file_exists = os.path.exists(file_full_path)

    # Create directory if it doesn't exist
    if not dir_exists:
        os.makedirs(directory)
        os.makedirs(archive_directory)
    # if directory exists and file exists copy old file to archive
    elif dir_exists:
        if file_exists:
            # if the file exists read the first line to get the date
            with open (file_full_path) as f:
                date = f.readline()
                date = date.replace(":","_")
                date = date.replace(" ","_")
                date = date[:-1]
                #print(date)
            new_file_path = archive_directory+'/'+config_type+'_'+date+'.txt'
            shutil.copy(file_full_path,new_file_path)
        elif not file_exists:
            pass
        else:
            print('ERROR in directory creation')
    else:
        print ('ERROR in directory creation')
    
    output_config = template.render(running_config=config_info,tstamp=tstamp)
    with open(file_full_path, 'w', encoding='utf8') as filehandler:
        filehandler.write(output_config)
        site_dict[site][name]['retrieved']=True

    # delete nonsense lines if this is from the config backup
    if config_type == 'running_config':
        with open(directory+'/'+'running_config.txt', 'r+', encoding='utf8') as fileprocessor:
            lines = fileprocessor.readlines()
            file_len = len(lines)
            fileprocessor.seek(0)
            fileprocessor.truncate()
            for number, line in enumerate(lines):
                if number not in [1, 2, 3, 4, file_len, file_len-1, file_len-2]:
                    fileprocessor.write(line)
    return

def retrieve_backup(central_info,serial,bu_name,name,site,site_dict,ticket,pre_post_type):
    """ Retrieve Backup """
    print ("Retrieve backup "+name)    
    backup_time = [] 

    s = requests.Session()
    retries = Retry(total=5,
    backoff_factor=2,
    status_forcelist=[ 502, 503, 504 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))
 
    access_token = central_info['token']['access_token']
    base_url = central_info['base_url']
    api_function_url = base_url + '/troubleshooting/v1/running-config-backup/serial/'+serial+'/prefix/'+bu_name
    qheaders = {
      "Content-Type":"application/json",
      "Authorization": "Bearer " + access_token,
    }

    response = s.request("GET", api_function_url, headers=qheaders)
    # get new token if token is expired and try again
    if (response.status_code == 401):
        central_info = test_central(central_info)
        response = s.request("GET", api_function_url, headers=qheaders)
        response_payload=(response.json())

    # if response is 200 all is good 
    elif (response.status_code == 200):
        response_payload=(response.json())

    # if response is something else return
    else:
        pprint(response.json())
        return central_info,site_dict

    #pprint(response_payload)
    for backup in response_payload:
        backup_name = backup['name']
        epoch_time = backup_name.split('.')[1]
        backup_time.append(epoch_time)

    #print(response_payload)
    latest_backup = max(backup_time)
    print ("Getting backup of time: "+latest_backup)
    latest_backup_name = bu_name+'.'+latest_backup+'.'+serial
    api_function2_url = base_url + '/troubleshooting/v1/running-config-backup/name/'+latest_backup_name
    response2 = s.request("GET", api_function2_url, headers=qheaders)

    # get new token if token is expired and try again
    if (response2.status_code == 401):
        central_info = test_central(central_info)
        response2 = s.request("GET", api_function2_url, headers=qheaders)
        response2_payload=(response2.json())
        if response2_payload['description'] == "Cannot get backup when in QUEUED state":
          print('Queued backup sleep 30 seconds')
          wait_for_it = True
          cycles = 0
          while wait_for_it and cycles < 10:
              time.sleep(30)
              cycles = cycles + 1
              response3 = s.request("GET", api_function2_url, headers=qheaders)
              if (response3.status_code == 401):
                  central_info = test_central(central_info)
                  response3 = s.request("GET", api_function2_url, headers=qheaders)
                  response3_payload=(response3.json())
              # response 200 ok move along
              elif (response3.status_code == 200):
                  response3_payload=(response3.json())
                  configuration = response3_payload['output']
                  tstamp = response3_payload['time']
                  wait_for_it = False
              elif (response3.status_code == 400):
                  response3_payload=(response3.json())
                  if response3_payload['description'] == "Cannot get backup when in QUEUED state":
                      wait_for_it = True
                  else:
                      print('internal error')
                      site_dict[site][name]['retrieved']=False
                      return central_info, site_dict
        else:
            print('internal error')
            site_dict[site][name]['retrieved']=False
            return central_info, site_dict
    # response 200 ok move along
    elif (response2.status_code == 200):
        response2_payload=(response2.json())
        configuration = response2_payload['output']
        tstamp = response2_payload['time']
    # if response 400 see if queued and then keep trying
    elif (response2.status_code == 400):
        response2_payload=(response2.json())
        if response2_payload['description'] == "Cannot get backup when in QUEUED state":
          print('Queued backup sleep 30 seconds')
          wait_for_it = True
          cycles = 0
          while wait_for_it and cycles < 10:
              time.sleep(30)
              cycles = cycles + 1
              response3 = s.request("GET", api_function2_url, headers=qheaders)
              if (response3.status_code == 401):
                  central_info = test_central(central_info)
                  response3 = s.request("GET", api_function2_url, headers=qheaders)
                  response3_payload=(response3.json())
              # response 200 ok move along
              elif (response3.status_code == 200):
                  response3_payload=(response3.json())
                  configuration = response3_payload['output']
                  tstamp = response3_payload['time']
                  wait_for_it = False
              elif (response3.status_code == 400):
                  response3_payload=(response3.json())
                  if response3_payload['description'] == "Cannot get backup when in QUEUED state":
                      wait_for_it = True
                      print('Queued backup sleep 30 seconds')
                  else:
                      print('internal error')
                      site_dict[site][name]['retrieved']=False
                      return central_info, site_dict
        else:
            print('internal error')
            site_dict[site][name]['retrieved']=False
            return central_info, site_dict
    else:
      print('internal error')
      site_dict[site][name]['retrieved']=False
      return central_info, site_dict

    config_type = 'running_config'
    write_out_config (serialnum=serial,config_type=config_type,config_info=configuration,
                       tstamp=tstamp,ticket=ticket,pre_post_type=pre_post_type,
                        name=name,site=site,site_dict=site_dict)
    return central_info, site_dict



