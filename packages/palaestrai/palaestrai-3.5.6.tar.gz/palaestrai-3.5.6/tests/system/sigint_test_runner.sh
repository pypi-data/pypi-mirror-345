#!/bin/bash

set -eux
timeout=${1:-3}
shift

echo "Current directory: $(pwd)"

palaestrai -v "$@" experiment-start ./tests/fixtures/dummy_run.yml &
pid=$!
sleep "$timeout"
kill -INT $pid
wait $pid
exit $?