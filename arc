#!/bin/bash

PYTHON="$(which python3)"

if [[ -x "$PYTHON" ]];
then
    $PYTHON archon.py "$@"
else
    echo  "Python 3 is required, exiting..."
fi
