import difflib
import os
import argparse
import sys
import yaml
from pprint import pprint
from time import gmtime, strftime

def compare (old_template_group,new_template_group,old,new,output_path):
    """ see if there is a diff if so print a file with diff """
    try:                    
        with open (old) as f:
            old_template_config = f.readlines()
        with open (new) as f:
            new_template_config = f.readlines() 
        difference2 = difflib.HtmlDiff(tabsize=2,wrapcolumn=80)
        print(output_path)
        with open(output_path, "w") as fp:
            html = difference2.make_file(fromlines=old_template_config, tolines=new_template_config, 
                                        fromdesc="Old Template Config - "+old_template_group, todesc="New Template Config -"+ new_template_group, context="True", numlines=5)
            fp.write(html)
    except:
        print('error')
    return

def map_out_comparisons(old_template_group,new_template_group, template_directory):
    """ Create compare dictionary """
    full_dict = {}
    all_versions = {}

    old_temp_loc = template_directory+'/'+old_template_group
    new_temp_loc = template_directory+'/'+new_template_group
    old_template = (os.listdir(old_temp_loc))
    new_template = (os.listdir(new_temp_loc))

    if len(old_template) == 1 and len(new_template) == 1:
        old_name = (old_template)[0]
        new_name = (new_template)[0]
        all_versions['old']=template_directory+'/'+old_template_group+'/'+old_name
        all_versions['new']=template_directory+'/'+new_template_group+'/'+new_name
    else:
        print("Exception Encountered Finding Templates")

    if all_versions != {}:
        full_dict['all_versions']=all_versions
    #pprint (full_dict)

    return full_dict

def main():
    """ Main function """
    url_file_loc = "central_url_info.yml"
    url_info = {}
    template_compare_dict = {}
    tstamp=strftime("%Y-%m-%d_%H_%M_%S", gmtime())

    try:
        with open(url_file_loc, "r") as fileinfo:
            url_info = yaml.safe_load(fileinfo.read())
    except Exception as err:
        print("Error: ",str(err))
    customer = url_info['central_customer']
    report_directory = 'diff_report/'+customer
    template_directory = 'scraped_data/'+customer+'/template_data'
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', required=True, dest='old_template_group', help='REQUIRED - Old Template Group')
        parser.add_argument('-n', required=True, dest='new_template_group', help='REQUIRED - New Template Group')   
        args = parser.parse_args()
        old_template_group = args.old_template_group
        new_template_group = args.new_template_group

    except:
        parser.print_help()
        sys.exit(0)

    template_compare_dict = map_out_comparisons(old_template_group,new_template_group,template_directory)
    report_name = report_directory+'/'+old_template_group+'----'+new_template_group+'.html'
    dir_exists = os.path.exists(report_directory)
    report_exists = os.path.exists(report_name)
    
    # Create output directory if it doesn't exist
    if not dir_exists:
        os.makedirs(report_directory)
    # if report exists rename it
    if report_exists:
        new_name = report_directory+'/'+old_template_group+new_template_group+tstamp+'.html'
        os.rename(report_name,new_name)

    for entry in template_compare_dict:
        old = template_compare_dict[entry]['old']
        new = template_compare_dict[entry]['new']
        output_path = report_name
        compare(old_template_group,new_template_group,old,new,output_path)

if __name__ == "__main__":
    main()