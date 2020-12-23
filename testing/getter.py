import requests, os


def issue_get(host, path, session):
    url = 'http://{}/{}'.format(host, path)
    referer = 'http://{}/{}'.format(host, os.path.dirname(path))
    print('url: {}'.format(url))
    print('referer: {}'.format(referer))
    print('host: {}'.format(host))
    response = requests.get(url,
        headers={'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Connection': 'keep-alive',
            'Cookie': 'hide-dotfile=no; session={}'.format(session),
            'Host': host,
            'Range': 'bytes=0-',
            'Referer': referer,
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 13421.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.199 Safari/537.36'
        }
    )
    return(response)


def get_stream_pi(session):
    host = '192.168.1.16:5000'
    path = 'kelly_rr_to_gryphon_run.mp4'
    return(issue_get(host, path, session))


def get_stream_nas(session):
    host = '192.168.1.73:5000'
    path = 'shared/Gopro/GH010004.mp4'
    return(issue_get(host, path, session))


if __name__ == '__main__':
    with open('session', 'r') as f:
        session = f.read().strip()
    response = get_stream_pi(session)
    print('got {} bytes'.format(len(response.content)))
