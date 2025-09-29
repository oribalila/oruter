#!/bin/bash

parent_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )"; pwd -P )
source $parent_path/lab_connect.sh

alias "lab-up"="bash $parent_path/up.sh"
alias "lab-down"="bash $parent_path/down.sh"
alias "lab-connect"="lab_connect"
