import yaml
import os
import getpass
import argparse
import sys
from pprint import pprint
from validate_central import test_central
from get_serials import get_serials_site
from kickoff_backup import kickoff_individual_backup
from retrieve_backup import retrieve_backup
from get_variables import get_variables

def set_initial_central_info (url_file_loc, access_token_raw, refresh_token_raw):
    """ Set Central Data return data """
    url_info = {}
    central_info_func = {}
    try:
        with open(url_file_loc, "r") as fileinfo:
            url_info = yaml.safe_load(fileinfo.read())
    except Exception as err:
        print("Error: ",str(err))
    access_token = {'access_token': access_token_raw }
    refresh_token = {'refresh_token': refresh_token_raw }
    central_customer = url_info['central_customer']
    base_url = url_info['central_info']['base_url']
    central_info_func['base_url'] = base_url
    central_info_func['customer_id'] = url_info['central_info']['customer_id']
    central_info_func['client_id'] =  url_info['central_info']['client_id']
    central_info_func['client_secret'] =  url_info['central_info']['client_secret']
    central_info_func['token'] = access_token
    central_info_func['refresh_token'] = refresh_token
    return central_info_func, central_customer

def main():
    """ Main function to kick off backup """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', required=True, dest='ticket', help='REQUIRED - Ticket Number')
        parser.add_argument('-p', required=True, dest='pre_post_type', help='REQUIRED - Check Type = pre or post')
        parser.add_argument('-s', required=True, nargs="+", 
                            dest='list_of_sites', help='REQUIRED list of sites being updated')     
        args = parser.parse_args()
        ticket = args.ticket
        pre_post_type = args.pre_post_type
        list_of_sites = args.list_of_sites
    except:
        parser.print_help()
        sys.exit(0)  

    directory= 'change_data/'+ticket
    bu_name = ticket + pre_post_type
    access_token_raw = getpass.getpass("Please provide the auth token: ")
    refresh_token_raw = getpass.getpass("Please provide the refresh token: ")

    # get central info
    url_file_loc = "inputs/central_credentials.yml"
    central_all_info = set_initial_central_info(url_file_loc, access_token_raw, refresh_token_raw)
    initial_central_info = central_all_info[0]

    # test central access
    central_info = test_central (initial_central_info)

    try:
        os.makedirs(directory)
    except:
        pass

    site_dict={}
    if list_of_sites != None:
        for site in list_of_sites:
            site = site
            serial_info=get_serials_site(central_info,site)
            site_dict[site]=serial_info[0]
            central_info = serial_info[1]
            for switch in site_dict[site]:
                device = site_dict[site][switch]['serial']
                site_dict[site][switch]['variables'] = get_variables(central_info,device) 
                if site_dict[site][switch]['status'] == 'Up':
                    kickoff_individual_backup (central_info,device,bu_name)
    else:
        pass

    pprint(site_dict)
    for site in list_of_sites:
        site = site
        for switch in site_dict[site]:
            serial = site_dict[site][switch]['serial']
            if site_dict[site][switch]['status'] == 'Up':
                 device = site_dict[site][switch]['serial']
                 name = switch
                 try:
                    go_fetch = retrieve_backup (central_info,serial,bu_name,name,site,site_dict,ticket,pre_post_type)
                    site_dict = go_fetch[1]
                    central_info = go_fetch[0]
                 except:
                    pass

    pprint(site_dict)
    output_name = pre_post_type+'_switch_info.yml'
    with open(directory+'/'+output_name, 'w') as f:
        yaml.dump(site_dict, f, sort_keys=False, default_flow_style=False)

if __name__ == "__main__":
    main()
   