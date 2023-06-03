#!/bin/bash

PYTHON="$(which python3)"
export PATH="$PATH:."
clear

if [[ -x "$PYTHON" ]];
then
    hypercorn --config hypercorn.toml runhttp:webapp --proxy-headers
else
    echo  "Python 3 is required, exiting..."
fi
