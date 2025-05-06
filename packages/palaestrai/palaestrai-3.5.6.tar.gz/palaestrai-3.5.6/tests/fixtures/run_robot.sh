#!/bin/bash

set -e
# better logging
set -xv

# $1: env reports dir ({toxinidir}/test_reports/{envname})
# $2: tests dir ({toxinidir}/tests)
# $3: stage variable (e.g. integration-src)

mkdir -p "$1" || true
mkdir -p "$2/$3" || true

# Source: https://stackoverflow.com/a/45729843
# Don't stop and also save exit status
ROBOT_RC=0
robot --argumentfile "$2/../fixtures/robot_argument_file.txt" --variable "stage:$3" --outputdir "$1" "$2" || ROBOT_RC=$?
rebot --argumentfile "$2/../fixtures/robot_keyword_argument_file.txt" -l "$1/log_enhanced.html" -o "$1/output_enhanced.xml" "$1/output.xml"
exit $ROBOT_RC