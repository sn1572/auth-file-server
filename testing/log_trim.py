import os, re


logfile = os.path.join('../log.txt')
outfile = 'log.trim'


if __name__ == '__main__':
    with open(logfile, 'r') as f:
        lines = f.readlines()
    r = re.compile('get range finds')
    r2 = re.compile('OSError')
    with open(outfile, 'w') as f:
        for line in lines:
            m = r.match(line)
            m2 = r2.search(line)
            if m or m2:
                f.write(line)
