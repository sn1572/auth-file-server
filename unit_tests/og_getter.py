import requests


def get_stream():
    URL = 'http://192.168.1.73:5000/shared/Gopro/GH010004.mp4'
    response = requests.get(URL,
        headers={'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Connection': 'keep-alive',
            'Cookie': 'hide-dotfile=no; session=.eJwljrEOwyAMBf-FuUP8DAbnZyKwjdo1aaaq_16kzncn3Scd84zrmfb3eccjHS9Pe7I5zA3KXgFmqcZ5-BgU2kVRkHuNRltwUFV4CZQo8IZSEFozNRL3mW1TJ15kSQZU584g7bN7UTbJdXXU4LINE1HNmh2S1sh9xfm_ofT9AaTGLlo.X8WPNA.Ntf30KRhODxQEd4kwXF6xw4ikjI',
            'Host': '192.168.1.73:5000',
            'Range': 'bytes=0-',
            'Referer': 'http://192.168.1.73:5000/shared/Gopro/',
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 13421.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.199 Safari/537.36'
        }
    )
    return(response)
