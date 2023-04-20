# goRunCommands #

## What is this repository for? ##

This repository contains a Go Script that can run commands on a device to gather pre and post checks.

## How do I get set up? ##

Click on the goDoTestPlan.exe and answer the questions.
First question: username
Second Question: ssh password
Third Question: Pre or Post ---> this should the type of check being run

## What are the data requirements ##

Make sure that whatever checks you wish to run are entered in the file:
inputs/commands.yml
--> make sure to add a sleep at the end to ensure data is collected
--> a no page should also be added at the beginning
--> an example is preserved

Also the switch list needs to be provided in the file
inputs/switch_list.yml
--> an example has been provided
--> the group does determine types of checks that are run, if the group is 'router' the router checks will be run otherwise only the other commands will be collected

## Script Descriptions ##

## goDoTestPlan

This script runs the commands specified on the switches specified. The user must provider username and ssh password when run.