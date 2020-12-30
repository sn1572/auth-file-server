from flask import Flask, Response
from flask.views import MethodView
from uwsgi import sharedarea_read, sharedarea_write


app = Flask(__name__)


class PathView(MethodView):
    def get(self, p=''):
        byte_string = bytes('byte string'.encode('utf-8'))
        sharedarea_write(0, 0, byte_string)
        test_bytes = sharedarea_read(0, 0, len(byte_string))
        html = '''
        <body>
        <p>This is a test. These are the bytes read from shared_area: {}</p>
        </body>
        '''.format(test_bytes)
        return(Response(html, mimetype="text/html"))


path_view = PathView.as_view('path_view')
app.add_url_rule('/', view_func=path_view)
