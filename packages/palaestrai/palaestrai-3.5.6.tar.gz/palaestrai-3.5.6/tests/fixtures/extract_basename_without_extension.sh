#!/bin/bash
echo "$(b=${1##*/}; echo ${b%.*})"