#!/bin/bash


# This script tries to locate the git project root and will
# either activate the Python environment found there or 
# create one if it does not exist. If we can't find the
# git project root dir then we just quit. I'm not going
# to do all the work for you. :)
# The last 3 lines of this script are all that's really essential.
# We need to issue the required .ini to uwsgi which will run
# Python. The Python should have the right environment to run the
# Flask server.


try_activate() {
    if [ -d "$1/pyenv" ];
    then
        source $1/pyenv/bin/activate
    else
        echo "Creating Python virtual environment at $1/pyenv."
        python3 -m venv $1/pyenv
        source $1/pyenv/bin/activate
        pip3 install -r $1/requirements.txt
    fi
}


python3 --version > /dev/null
if [ "$?" != "0" ];
then
    echo "No working version of Python3 found. Quitting."
    exit 1
fi

PATH_TO_GIT_ROOT=$(python3 -c \
"import os
path = os.getcwd()
index = path.index('auth-file-server')
path = path[index:].split('/')
if len(path) == 1:
    print('.')
else:
    path = (len(path) - 1) * '../'
    print(path[:-1])")

if [ "$?" != "0" ];
then
    echo "Could not locate project root directory. Quitting."
    exit 1
fi

try_activate $PATH_TO_GIT_ROOT
CONFDIR=${PATH_TO_GIT_ROOT}/uwsgi_configs
uwsgi --ini ${CONFDIR}/lan_config.ini
