import difflib
import os
import argparse
import sys
import yaml
from time import gmtime, strftime
from pprint import pprint
from jinja2 import Environment, FileSystemLoader

def compare (directory,pre_running_file,post_running_file,device,differences,no_differences,error_state,tstamp):
    """ see if there is a diff if so print a file with diff """
    print (pre_running_file)
    print (post_running_file)
    try:                
        with open (post_running_file) as f:
            post_running_config = f.readlines()
            #print(post_running_config)
        with open (pre_running_file) as f:
            pre_running_config = f.readlines()
            #print(pre_running_config)        
            #running_config = f.readlines()
     
        differences=differences.append(device)
        difference2 = difflib.HtmlDiff(tabsize=2,wrapcolumn=80)
        file_name=directory+'/'+device+'cli_diff'+'.html'
        with open(file_name, "w") as fp:
                html = difference2.make_file(fromlines=pre_running_config, tolines=post_running_config, 
                                            fromdesc="Pre Change - ", 
                                            todesc="Post Change - ",
                                            context="True", numlines=5)
                fp.write(html)       
    except:
        print('error')
        error_state=error_state.append(device)
    return

def get_list_of_devices (ticket):
    config_dumps = 'change_data/'+ticket
    switch_list = [name for name in os.listdir(config_dumps) if (os.path.isdir
                  (os.path.join(config_dumps, name)) and 'bak' not in name)]
    return switch_list  

def make_final_report (directory,differences,no_differences,error_state,tstamp,device_dictionary,var_diff):
    """Template out report"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('cli_report_html.j2')
    final_report = template.render(differences=differences,no_differences=no_differences,error_state=error_state,
                                    device_dictionary=device_dictionary)
    with open(directory+'/'+'cli_report'+'.html', 'w', encoding='utf8') as filehandler:
        filehandler.write(final_report)
    print ('Report is stored here: '+ directory)
    return

def main():
    """ Main function """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', required=True, dest='ticket', help='REQUIRED - Ticket Number')    
        args = parser.parse_args()
        ticket = args.ticket
    except:
        parser.print_help()
        sys.exit(0)  
  
    # Create directory to store report and diffs
    tstamp=strftime("%Y-%m-%d_%H_%M_%S", gmtime())
    directory= 'change_data/'+ticket

    list_of_devices = get_list_of_devices(ticket)

    with open(directory+'/pre_switch_info.yml', 'r') as file:
        pre_info = yaml.load(file, Loader=yaml.SafeLoader)

    with open(directory+'/post_switch_info.yml', 'r') as file:
        post_info = yaml.load(file, Loader=yaml.SafeLoader)

    device_dictionary = {}
    for site in pre_info:
        for switch in pre_info[site]:
            device_dictionary[switch]={}
            device_dictionary[switch]['pre']={}
            device_dictionary[switch]['pre']=pre_info[site][switch]
    for site in post_info:
        for switch in post_info[site]:
            device_dictionary[switch]['post']={}
            device_dictionary[switch]['post']=post_info[site][switch]
            
    no_differences = []
    differences = []
    error_state = []
    var_diff={}

    for device in list_of_devices:
        pre_running_file = 'change_data/'+ticket+'/'+device+'-PRE/portinfo.txt'
        post_running_file = 'change_data/'+ticket+'/'+device+'-POST/portinfo.txt'
        compare (directory,pre_running_file,post_running_file,device,differences,no_differences,error_state,tstamp)

    print ("DEVICES WITH DIFFERENCES")
    print(differences)
    print('----')
    print ("DEVICES WITH NO DIFFERENCES")
    print(no_differences)
    print('----')
    print ("DEVICES WITH COMPARE ERROR")
    print(error_state)
    make_final_report(directory,differences,no_differences,error_state,tstamp,device_dictionary,var_diff)

if __name__ == "__main__":
    main()