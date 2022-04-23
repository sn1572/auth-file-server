import subprocess as sub
import os
import configparser
import random


reports = []
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'uwsgi_configs',
                         'afs.ini'))
config = config['afs']


def agg(f):
    #Janky but tricky way of doing this
    global reports
    reports.append(f)
    return(f)


@agg
def get_root_usage():
    #Gets root fs usage
    fs_path = config['fs-path']
    fs_path = fs_path.replace('/', '\/')
    fs_nickname = config['fs-nickname']
    out = sub.check_output('df | awk \'/'+\
        fs_path+'/ {print $5}\'', shell=1)
    out = out.decode('utf-8').strip()
    return("{} file system usage: {}".format(fs_nickname, out))


@agg
def get_kernel_version():
    out = sub.check_output('uname -r', shell=1).decode('utf-8').strip()
    return("Kernel version: {}".format(out))


@agg
def plex_hatred():
    current_dspp = random.randint(1,10)
    level_map = {0: 'un-disappointed',
        1: 'they forgot napkins in your happy meal',
        2: 'cloudy day',
        3: 'missed a spot while cleaning glass',
        4: 'your bust is delayed 15 minutes',
        5: 'item out of stock; refund issued - after 5 days',
        6: 'windows update during work presentation',
        7: 'Mr. Lahey with a whiskey dick after getting back with Randy',
        8: 'Linus Torvalds being told Nvidia don\'t contribute FOSS drivers',
        9: 'Dennis Ritchie realizing your compiler is not ANSII compliant',
        10: 'like a Kernel developer discovering your tainted kernel'}
    return("Current disappointment in Plex: {}/10 ({})".format(
        current_dspp,
        level_map[current_dspp]))


def net_usage_pie():
    adapter = 'eth0'
    img_file = './assets/abt-img/network-log-pie.png'
    if not os.path.isdir('assets/abt-img'):
        os.mkdir('assets/abt-img')
    _ = sub.check_output('vnstati -s -i {} -o {}'.\
        format(adapter, img_file), shell=1)
    return('')


def net_usage_bar():
    adapter = 'eth0'
    img_file = './assets/abt-img/network-log-bar.png'
    if not os.path.isdir('assets/abt-img'):
        os.mkdir('assets/abt-img')
    _ = sub.check_output('vnstati -h -i {} -o {}'.\
        format(adapter, img_file), shell=1)
    return('')


reports = list(map(lambda f: f(), reports))
