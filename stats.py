import subprocess as sub


reports = []


def agg(f):
    #Janky but tricky way of doing this
    global reports
    reports.append(f)
    return(f)


@agg
def get_root_usage():
    #Gets root fs usage
    out = sub.check_output('df | awk \'/\/dev\/root/ {print $5}\'', shell=1)
    out = out.decode('utf-8').strip()
    return("Root file system usage: {}".format(out))


@agg
def get_kernel_version():
    out = sub.check_output('uname -r', shell=1).decode('utf-8').strip()
    return("Kernel version: {}".format(out))


@agg
def plex_hatred():
    current_dspp = 7
    level_map = {0: 'un-disappointed',
        1: 'they forgot napkins in your happy meal',
        2: 'cloudy day',
        3: 'missed a spot while cleaning',
        4: '15 minute delay',
        5: 'item out of stock; refund issued',
        6: 'windows update during work presentation',
        7: 'Lahey with a whiskey dick',
        8: 'Linus Torvalds doesn\'t have time to see you',
        9: 'Dennis Ritchie locked his office door',
        10: 'like a kernel developer being told you run a tainted kernel'}
    return("Current disappointment in Plex: {}/10 ({})".format(
        current_dspp,
        level_map[current_dspp]))


@agg
def net_usage_pie():
    adapter = 'wlan0'
    img_file = './assets/abt-img/network-log-pie.png'
    _ = sub.check_output('vnstati -s -i {} -o {}'.\
        format(adapter, img_file), shell=1)
    return('')


@agg
def net_usage_bar():
    adapter = 'wlan0'
    img_file = './assets/abt-img/network-log-bar.png'
    _ = sub.check_output('vnstati -h -i {} -o {}'.\
        format(adapter, img_file), shell=1)
    return('')


reports = list(map(lambda f: f(), reports))
