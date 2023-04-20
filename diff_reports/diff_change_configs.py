import difflib
import os
import argparse
import sys
import yaml
from time import gmtime, strftime
from pprint import pprint
from jinja2 import Environment, FileSystemLoader

def ignore_things(line):
    things_to_ignore = ['Troubleshooting','user admin group administrators password','user operator group operators password']
    if line.startswith ('!'):
        return False
    for thing in things_to_ignore:
        if thing in line:
            #print(line)
            return False
    return True

def compare (directory,pre_running_file,post_running_file,device,differences,no_differences,error_state,tstamp):
    """ see if there is a diff if so print a file with diff """
    print (pre_running_file)
    print (post_running_file)
    try:
        with open (pre_running_file) as f:
            pre_running_time = f.readline()
            #print(pre_running_time)
        with open (post_running_file) as f:
            post_running_time = f.readline()
            #print(post_running_time)                     
        with open (post_running_file) as f:
            post_running_config = f.readlines()[1:]
            #print(post_running_config)
        with open (pre_running_file) as f:
            pre_running_config = f.readlines()[1:]  
            #print(pre_running_config)        
            #running_config = f.readlines()
            
        f1 = filter(ignore_things, pre_running_config)
        f2 = filter(ignore_things, post_running_config)
        the_same = (all(x == y for x, y in zip(f1, f2))) 

        if not the_same:       
            differences=differences.append(device)
            difference2 = difflib.HtmlDiff(tabsize=2,wrapcolumn=80)
            file_name=directory+'/'+device+'_diff'+'.html'
            with open(file_name, "w") as fp:
                html = difference2.make_file(fromlines=pre_running_config, tolines=post_running_config, 
                                            fromdesc="Pre Running Config - "+str(pre_running_time), 
                                            todesc="Post Running Config - "+str(post_running_time),
                                            context="True", numlines=5)
                fp.write(html)
        elif the_same:
            no_differences=no_differences.append(device)
        else:
            print('error')        
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
    template = env.get_template('final_report_html.j2')
    final_report = template.render(differences=differences,no_differences=no_differences,error_state=error_state,
                                    device_dictionary=device_dictionary,var_diff=var_diff)
    with open(directory+'/'+'final_report'+'.html', 'w', encoding='utf8') as filehandler:
        filehandler.write(final_report)
    print ('Report is stored here: '+ directory)
    return

def compare_variables(vars_pre,vars_post):
    var_diff = {}
    values_changed = []
    new_key = []
    deleted_key = []
    for k in vars_pre:
        if k in vars_post:
            if vars_pre[k]==vars_post[k]:
                pass
            else:
                cgd = k+' - Pre: '+vars_pre[k]+' / Post: '+vars_post[k]
                values_changed.append(cgd)
        else:
            rm = k+': '+vars_pre[k]
            deleted_key.append(rm)
    for k in vars_post:
        if k not in vars_pre:
            add = k+': '+vars_post[k]
            new_key.append(add)
    var_diff['variables_changed'] = values_changed
    var_diff['new_variables'] = new_key
    var_diff['deleted_variables'] = deleted_key
    #var_diff = DeepDiff(vars_pre,vars_post)
    pprint(var_diff)
    return var_diff


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
        pre_running_file = 'change_data/'+ticket+'/'+device+'/pre/running_config.txt'
        post_running_file = 'change_data/'+ticket+'/'+device+'/post/running_config.txt'
        preserial=device_dictionary[device]['pre']['serial'] 
        postserial=device_dictionary[device]['pre']['serial'] 
        pre_vars = device_dictionary[device]['pre']['variables'][preserial]
        post_vars = device_dictionary[device]['post']['variables'][postserial]
        #pprint(pre_vars)
        #pprint(post_vars)
        var_diff[device]=compare_variables(pre_vars,post_vars)
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