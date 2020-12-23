#!/bin/bash


source pyenv/bin/activate

#uwsgi --http :5000 --module file_server:app
uwsgi --ini uwsgi_config.ini
