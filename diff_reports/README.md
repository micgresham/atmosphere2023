# change-tools

This repository contains tools that will make it easier for change validations.

### What is this repository for? ###
#### change_get_configs.py
This script will take a ticket number, change type, and site list and retrieve configurations. The configuration will be stored in the directory change_data/{{ticket}}/{{pre_or_post}}

Also generated is a file that contains information about each switch. It is saved under change_data/{{ticket}}/{{pre_or_post}}_switch_info.yml

To run the script specify the following:
-s = list of sites being changed
-t = ticket number
-p = pre or post -- the configurations being gathered pre if pre change post if post change

You will be asked for your Central API token when running the script. 

Note, that for the API Refresh token to work your client secret should be stored in inputs/central_credentials.yml. It is recommended that this be vaulted.

To run:
```
python3 change_get_configs.py -s {{list of sites}} -t {{ticket}} -p {{pre or post}}
```

Example:
```
python3 change_get_configs.py -s LEANDER-LAB -t salesports -p pre
```

#### change_diff_configs.py
This script will take a ticket number and produce a report. This script can only be run after a pre and post is collected with change_get_configs.py. It must be run on the same machine where the pre and post change collection script was run as it compares the files collected in change_data/{{ticket}}/pre and change_data/{{ticket}}/post. The reports produced are stored in change_data/{{ticket}} and are final_report.html which is a summary of all devices and if there are any differences there is also a diff file for each device {{device-name}}_diff.html. 

To run:
```
python3 diff_change_configs.py -t {{ticket}}
```

Example:
```
python3 diff_change_configs.py -t salesports
```
#### diff_change_cli.py
This script will take the CLI state information gathered and compare pre and post. There is another repository goRunCommands that can be used to get the data. Then move the pre and post folders to the directory with the change ticket.

To run:
```
python3 diff_change_cli.py -t {{ticket}}
```

Example:
```
python3 diff_change_cli.py -t salesports
```

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Michael Gresham - michael.gresham@hpe.com
* Sarah Tovar - sarah.tovar@hpe.com
