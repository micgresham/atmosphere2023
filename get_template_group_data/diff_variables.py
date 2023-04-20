import os
import argparse
import sys
import yaml
from pprint import pprint
from jinja2 import Environment, FileSystemLoader

def make_final_report (report_name,html_contents,variable,template_group):
    """Template out report"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('final_report_html.j2')
    final_report = template.render(html_contents=html_contents,variable=variable,
                                    template_group=template_group)
    with open(report_name+'.html', 'w', encoding='utf8') as filehandler:
        filehandler.write(final_report)
    print ('Report is stored here: '+ report_name)
    return

def main():
    """ Main function """
    url_file_loc = "central_url_info.yml"
    url_info = {}

    try:
        with open(url_file_loc, "r") as fileinfo:
            url_info = yaml.safe_load(fileinfo.read())
    except Exception as err:
        print("Error: ",str(err))
    customer = url_info['central_customer']
    report_directory = 'variable_report/'+customer
    template_directory = 'scraped_data/'+customer+'/template_data'
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-g', required=True, dest='template_group', help='REQUIRED - Template Group')
        parser.add_argument('-v', required=True, dest='variable', help='REQUIRED - Variable')   
        args = parser.parse_args()
        template_group = args.template_group
        variable = args.variable
    except:
        parser.print_help()
        sys.exit(0)

    report_name = report_directory+'/'+variable+'--'+template_group
    # Make sure template group exists
    template_group_dir = template_directory+'/'+template_group
    try:
        template = (os.listdir(template_group_dir))
    except:
        sys.exit("No information for that template group - EXITING")
    if len(template) == 1:
        temp_name = (template)[0]
        template_location = template_group_dir+'/'+temp_name
    else:
        sys.exit('No template collected for that group - EXITING')

    pprint(template_location)
    with open (template_location) as f:
        template_config = f.readlines()

    html_contents = []
    var_in_file = '%'+variable+'%'
    var_with_if = '%if '+variable
    for line in template_config:
        if var_in_file in line:
            html_contents = html_contents + ['<mark>'+line+'</mark>']
        elif var_with_if in line:
            html_contents = html_contents + ['<mark>'+line+'</mark>']
        else:
            html_contents = html_contents + [line]

    make_final_report(report_name,html_contents,variable,template_group)

if __name__ == "__main__":
    main()