#!/bin/bash


source pyenv/bin/activate

CONFDIR=./uwsgi_configs
#uwsgi --http :5000 --module file_server:app
uwsgi --ini ${CONFDIR}/lan_config.ini
#uwsgi --init ${CONFDIR}/nginx_config.ini
