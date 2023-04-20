# README #

This repository is meant to store templates used by Aruba Central for template groups. It has Ansible Plays to create/enforce template md5 checksums and to create template groups.

## What is this repository for? ##

* Storing templates and template data.
* There is also an Ansible Play that writes the hash data for each template if it is changed. 
* There is also an Ansible Play that handles the creation of CX and IAP template groups.

## How do I get set up? ##

* Python and Ansible need to be installed on the machine where it is run

### Ansible Requirements ###

* Python3 must be installed

**#### Debian linux install steps ####**
```
sudo apt update
sudo apt-get install python3
sudo apt-get install python3-pip
``` 

**#### Mac ####**

You can get python from https://www.python.org/downloads/macos/

**#### Windows ####**

Ansible doesn't work natively on Windows, if running this on a Windows machine, the following should be done:

* Run on a vm running linux

* Set up a WSL environment - preferred method - for install steps https://docs.microsoft.com/en-us/windows/wsl/setup/environment easiest on Windows Build 20262+ with powershell 
command 

```
wsl --install
```

Note recommended to use a Debian based option such as Ubuntu - I would highly recommend using Ubuntu 20.04

**#### Optional virtual environment ####**

A virtual environment is recommended for running the script so it will be set up appropriately

Once python has been installed -- NOTE if running Ubuntu 22.x see the below steps to get the virtual environment working
```
pip install virtualenv

Then from within the directory of the repo
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
ansible-galaxy install arubanetworks.aruba_central_role
ansible-galaxy install -r galaxy.yml
```

**#### Ubuntu 22.x steps ####**
Note, all the steps above will work for Ubuntu 20.x, but if you are running Ubuntu 22.x use the following steps to get the virtual environment set up:

```
sudo apt update
sudo apt-get install python3
sudo apt install python3-pip
sudo mkdir /usr/local/bin
sudo ln -s /usr/bin/virtualenv /usr/local/bin/virtualenv

Then from within the directory of the repo:

sudo virtualenv venv
source venv/bin/activate
sudo pip3 install -r requirements.txt
sudo ansible-galaxy install -r galaxy.yml
sudo ansible-galaxy install arubanetworks.aruba_central_role

Note, all ansible plays going forward should be run as sudo!

```


### Steps Once Ansible is installed for template update ###

If creating or updating a template in the pilot branch, the following steps must be completed:

** note, if running on ubuntu 22 and the above steps were followed, run all commands as sudo **

1. Copy the config file being updated/created from the main branch and place it in the new_templates folder - the version does not need to be updated just ensure the header and footer with the template version exist - multiple templates of the same type (cx or iap) can be updated at once. Also, make sure to only modify the regular all code versions form of the CX template.

2. Run generate_info.yml of the correct type - only run one type at a time - note multiple templates though can be updated at once as long as they are all of the same type such as all cx or all iap
```
If running from a virtual environment, activate the virtual environment first:
    source venv/bin/activate

Then run the appropriate play per device type:
    ansible-playbook generate_info_cx.yml
    ansible-playbook generate_info_iap.yml

If you want to just run a test run with extra-var testmode - this will create a test directory so you can review contents without changing
example: ansible-playbook generate_info_cx.yml --e testmode='y'

When done if using a virtual environment deactivate the virtual environment:
    deactivate
```

3. The play will then increment the version number in the template_data.yml file, add the md5checksum, move the existing file to the archive (if it exists)

4. Update the correct changelog in changelogs/changelog - <TYPE> with pertinent information about the change and the new version 

5. When ready you can create groups too!


### Steps Once Ansible is installed for generate_groups_cx.yml ###

In order to create CX template groups, perform the following steps:
1. Make sure the groups being added are in inputs/groups.yml
   --> note, there is a sample with explanation text as to how this should be done named inputs/sample_groups.yml
2. Make sure the information is correct in the inventory.yml file - Note the ansible_host should be the URL for Central

To run:
```
If running from a virtual environment, activate the virtual environment first:
    source venv/bin/activate
    pip install -r requirements.txt
    ansible-galaxy install -r galaxy.yml

Then run the play:
    ansible-playbook generate_groups_cx.yml -i inventory.yml

When done if using a virtual environment deactivate the virtual environment:
    deactivate
```

A few things to note:
* if any of the groups already exist, the play will fatally fail
* you will be asked for your token after the play is run, if your token fails, the play will fatally fail
* during the play run, the template hashes that the groups have is compared to the expected values, if they do not match, the play will fatally fail
* if multiple groups are being requested for the same template, 1 group will be created and then cloned with the correct names
* if running on Ubuntu 22. see the caveats listed above 

### Steps Once Ansible is installed for generate_groups_iap.yml ###

In order to create IAP template groups, perform the following steps:
1. Make sure the groups being added are in inputs/groups.yml
   --> note, there is a sample with explanation text as to how this should be done named inputs/sample_groups.yml
2. Make sure the information is correct in the inventory.yml file - Note the ansible_host should be the URL for Central

To run:
```
If running from a virtual environment, activate the virtual environment first:
    source venv/bin/activate
    pip install -r requirements.txt
    ansible-galaxy install -r galaxy.yml

Then run the play:
    ansible-playbook generate_groups_iap.yml -i inventory.yml

When done if using a virtual environment deactivate the virtual environment:
    deactivate
```

A few things to note:
* if any of the groups already exist, the play will fatally fail
* you will be asked for your token after the play is run, if your token fails, the play will fatally fail
* during the play run, the template hashes that the groups have is compared to the expected values, if they do not match, the play will fatally fail
* if multiple groups are being requested for the same template, 1 group will be created and then cloned with the correct names
* if running on Ubuntu 22. see the caveats listed above 


## Contribution guidelines ##

* Writing tests
* Code review
* Other guidelines

## Who do I talk to? ##

* Michael Gresham - michael.gresham@hpe.com
* Sarah Tovar - sarah.tovar@hpe.com