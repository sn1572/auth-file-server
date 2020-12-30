#!/bin/bash


source pyenv/bin/activate

CONFDIR=./uwsgi_configs
uwsgi --ini ${CONFDIR}/lan.ini
#uwsgi --ini ${CONFDIR}/nginx.ini
    #for the test script, first:
    #ln -s testing/shmem.py shmem_test.py
#uwsgi --ini ${CONFDIR}/testing.ini
