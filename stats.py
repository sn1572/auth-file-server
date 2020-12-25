import subprocess as sub


reports = []


def get_root_usage():
    #Gets root fs usage
    out = sub.check_output('df | awk \'/\/dev\/root/ {print $5}\'', shell=1)
    out = out.decode('utf-8').strip()
    print("Root file system usage: {}".format(out))


reports.append(get_root_usage())
