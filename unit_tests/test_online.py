import configparser
import requests
import socket


_test_file = 'shared/test.mp4'


def get_server_address():
    config = configparser.ConfigParser()
    config.read('../uwsgi_configs/lan_config.ini')
    port = config['uwsgi']['http']
    ip_addr = socket.gethostname()
    return f"{ip_addr}{port}/"


def test_get_stream():
    url = get_server_address()
    url += _test_file
    response = requests.get(url)
    print(response.headers)
