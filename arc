#!/bin/bash

PYTHON="$(which python3)"
ARCHONDIR="/opt/archon-server"

if [[ -x "$PYTHON" ]];
then
    cd $ARCHONDIR
    $PYTHON archon-cli.py "$@"
else
    echo  "Python 3 is required, exiting..."
fi
