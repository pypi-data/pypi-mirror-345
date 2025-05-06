#!/bin/bash
set -xv

sed -i -r "s/^store_uri:.*/store_uri: postgresql:\/\/$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST\/$POSTGRES_DB/g" /workspace/palaestrai.conf

palaestrai -c /workspace/palaestrai.conf database-create

cd /palaestrai || exit 1

palaestrai -c /workspace/palaestrai.conf experiment-start \
tests/fixtures/Classic-ARL-Experiment_run-0.yml