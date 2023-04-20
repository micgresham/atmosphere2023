# get_template_group_data #

## What is this repository for? ##

This repository is meant to store template text backups before we delete template groups. It is also used to diff the configuration between template groups.

## How do I get set up? ##

* Python needs to be installed on the machine where it is run. The requirements for the script are in the requirements.txt file.

* Python3 must be installed

**#### Debian linux install steps ####**
```
sudo apt update
sudo apt-get install python3
``` 

**#### Mac ####**

You can get python from https://www.python.org/downloads/macos/

**#### Windows ####**

* Setting up a WSL environment is the preferred method - for install steps https://docs.microsoft.com/en-us/windows/wsl/setup/environment easiest on Windows Build 20262+ with powershell 

command 

```
wsl --install
```

Note recommended to use a Debian based option such as Ubuntu

**#### Optional virtual environment ####**

A virtual environment is recommended for running the script so it will be set up appropriately

Once python has been installed
```
pip install virtualenv

Then from within the directory of the repo
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## What are the data requirements ##

the file central_url_info.yml must have the following information:
    central_info:
        base_url: "<Aruba Central URL>"
    central_customer: '<Friendly Customer Name>'

## Script Descriptions ##

## get_templates.py

Script that gathers template groups and templates from Aruba Central for the given customer. 

Templates and template information are stored under scraped_data/<CUSTOMER>/

Template text for a template group is stored under the name of the template scraped_data/<CUSTOMER>/<GROUP_NAME>/<TEMPLATE_NAME>
information about templates (including hash_ is stored under scraped_data/<CUSTOMER>/group_to_template.yml

Note, the customer collected is from the central_url_info.yml file
Requires API token at runtime.

## diff_template_configs.py

Script that does a diff between templates for given groups. Must specify -o for old template and -t for new template
The diff report is then stored in diff_report/<CUSTOMER>/oldtemp_newtemp.txt

Note, the customer compared is from the central_url_info.yml file

```
Example: 
python3 diff_template_configs.py -o LL-B-ACCESS-main-v4 -n LL-B-ACCESS-main-v5
```

## diff_variables.py

Script that highlights instances of a variable in an html format to make it easier to find
The diff report is then stored in variable_report/<CUSTOMER>/<var_name>-<template_name>.txt

Note, the customer compared is from the central_url_info.yml file

```
Example: 
python3 diff_variables.py -g LL-B-ACCESS-main-v5 -v sales_hardcode_speed
```
