#!/bin/bash

#pgrep palaestrAI | xargs kill -9 || true
#kill -9 $(ps aux | grep "palaestrai\|multiprocessing" | grep -v "robot\|pabot" | awk '{print $2}') || true
#kill -9 $(ps aux | grep ".*python.*robot.*CALLER_ID.*" | awk '{print $2}' | xargs -L 1 pgrep -P ) || true

# Get root pid to search recursively from
# The root pids are the child pids of the python-robot command, which actually executes the command as process from robotframework
ps aux | grep "/bin/sh -c palaestrai .*" | awk '{print $2}' | while read -r pid ; do
    # Kill all child process
    # Source: https://superuser.com/a/822450
    ps --forest --no-header $(ps -e --no-header -o pid,ppid|awk -vp=$pid 'function r(s){print s;s=a[s];while(s){sub(",","",s);t=s;sub(",.*","",t);sub("[0-9]+","",s);r(t)}}{a[$2]=a[$2]","$1}END{r(p)}') | awk '{print $1}' | xargs -L 1 kill -9
done
