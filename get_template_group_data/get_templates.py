import yaml,os,getpass,shutil
from pycentral.base import ArubaCentralBase
from pycentral.configuration import Groups
from pycentral.configuration import Variables
from pycentral.configuration import Devices
from pycentral.configuration import Templates
from pprint import pprint
from time import gmtime, strftime

def set_central_info (url_file_loc):
    url_info = {}
    central_info = {}
    try:
        with open(url_file_loc, "r") as fileinfo:
            url_info = yaml.safe_load(fileinfo.read())
    except Exception as err:
        print("Error: ",str(err))
    access_token_raw = getpass.getpass("Please provide the auth token: ")
    access_token = {'access_token': access_token_raw }
    
    central_info = url_info['central_info']
    central_info['token'] = access_token
    central_customer = url_info['central_customer']
    return central_info, central_customer

def get_all_groups (central):
    # set initial vars
    print ("Getting groups")
    limit = 20
    g = Groups()
    full_group_list = []

    # loop through call to get groups appending groups to full group list
    # stop when response is empty
    counter = 0
    need_more = True

    while need_more:
        response = g.get_groups(central,offset=counter,limit=limit)
        if response['msg']['data'] != []:
            full_group_list = full_group_list + response['msg']['data']
        elif response['msg']['data'] == []:
            need_more = False
            break
        else:
            print("ERROR")
            need_more = False
            print(response)
            break
        counter = counter + limit
        print(counter)
    full_group_list_flat = [item for sublist in full_group_list for item in sublist]
    return (full_group_list_flat)    

def get_group_to_template (central, group_list):
    print ("Getting group to template mapping")    
    # set initial vars
    t = Templates()
    group_to_template_dict = {}

    # loop over group list and get templates in each group - add to group_to_template_dict 
    for gp in group_list:
        print (gp)
        response = t.get_template(central,group_name=gp)
        if response['code'] == 404:
            group_to_template_dict[gp]='none'
        elif response['code'] == 200:
            group_to_template_dict[gp]=response['msg']['data']
        else:
            group_to_template_dict[gp]='none'
    return (group_to_template_dict) 

def get_template_text (central, group, template_name,directory):
    print ("Getting template text ",template_name)    
    # set initial vars
    t = Templates()
    temp_text = ''
    directory = directory+'/'+group

    file_name = template_name
    file_full_path = directory+'/'+file_name
    dir_exists = os.path.exists(directory)
    file_exists = os.path.exists(file_full_path)

    # Create directory if it doesn't exist
    if not dir_exists:
        os.makedirs(directory)
    # if directory exists and file exists delete old copy of file
    elif dir_exists:
        if file_exists:
            # if the file exists delete it
            os.remove(file_full_path)
        elif not file_exists:
            pass
        else:
            print('ERROR in directory creation')
    else:
        print ('ERROR in directory creation')

    # Get template text
    response = t.get_template_text(central,group_name=group,template_name=template_name)
    temp_text = response['msg']
    with open(file_full_path,'w') as f:
        f.write(temp_text)

    return        

# get auth info
url_file_loc = "central_url_info.yml"
file_info = set_central_info(url_file_loc)
central_info = file_info[0]
central_customer = file_info[1]
ssl_verify=True
directory = 'scraped_data/'+central_customer+'/template_data/'

time_stamp=strftime("%Y-%m-%d_%H_%M_%S"+"_UTC", gmtime())

#set Central data
central = ArubaCentralBase(central_info=central_info, ssl_verify=ssl_verify)

# get list of all groups
group_list = get_all_groups (central)

# get templates of each group
group_to_template_dict = get_group_to_template(central,group_list)
pprint(group_to_template_dict)

# get template text
for group in group_to_template_dict:
    print(group)
    try:
        for item in group_to_template_dict[group]:
            template_name = item['name']
            get_template_text(central,group,template_name,directory)
    except:
        print('Error on group: ',group)

# dump template data to file

output_name = 'group_to_template.yml'
output_path = directory+'/'+output_name
archive_directory = directory+'/archive'
archive_path = archive_directory+'/'+time_stamp+output_name
file_exists = os.path.exists(output_path)
dir_exists = os.path.exists(directory)
archive_dir_exists = os.path.exists(archive_directory)

# Create directory and archive if it doesn't exist
if not dir_exists:
    os.makedirs(directory)
    os.makedirs(archive_directory)
# if directory exists and file exists archive old copy of file
elif dir_exists:
    # create archive directory if it doesn't
    if not archive_dir_exists:
        os.makedirs(archive_directory)
    else:
        pass
    if file_exists:
        # if the file exists move it to the archive
        shutil.copy(output_path,archive_path)
    elif not file_exists:
        pass
    else:
        print('ERROR in data dump')
else:
    print ('ERROR in data dump')

with open(directory+'/'+output_name, 'w') as f:
    data = yaml.dump(group_to_template_dict, f, sort_keys=False, default_flow_style=False)
