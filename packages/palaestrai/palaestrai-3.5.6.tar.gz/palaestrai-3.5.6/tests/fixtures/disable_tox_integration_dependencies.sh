#!/bin/bash

# better logging
set -xv

# Source: https://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


sed -i 's/.*{\[cfg-integration-src\]deps}.*/    # {\[cfg-integration-src\]deps}/g' "${SCRIPT_DIR}/../../tox.ini"
sed -i 's/.*{\[cfg-integration-pypi\]deps}.*/    # {\[cfg-integration-pypi\]deps}/g' "${SCRIPT_DIR}/../../tox.ini"
