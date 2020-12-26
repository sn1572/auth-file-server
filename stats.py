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
    return("Disappointment in Plex: +++++++---")


reports = list(map(lambda f: f(), reports))
