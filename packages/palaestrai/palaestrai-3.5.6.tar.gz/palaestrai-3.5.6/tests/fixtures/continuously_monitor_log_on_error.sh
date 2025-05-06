#!/bin/bash

# Orig. Source: https://stackoverflow.com/a/7594930
# INPUT:
# $1: stdout log file to monitor
# $2: stderr log file to monitor
# $3: grep string to check on errors
# $4: sleep time
# OUTPUT
# rc: If 0: grep found error in logs
# stdout: error-lines from logs found by grep

# Source: https://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

while [[ true ]];
do
  sleep $4
  cat $1 $2 | grep "$3"
  if [[ $? -eq 0 ]]
  then
    /bin/bash "${SCRIPT_DIR}/kill_palaestrai_from_robot.sh"
    exit 0
  fi
done
