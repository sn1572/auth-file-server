from flask import Flask, make_response, request, session, Response, url_for
from flask import stream_with_context, render_template, send_file
from flask.views import MethodView
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import humanize, os, re, stat, json, mimetypes, sys
import subprocess as sub
from pathlib2 import Path
from flask_sqlalchemy import SQLAlchemy


root = os.path.normpath('server-root')

#app init and config settings
app = Flask(__name__, static_url_path='/assets', static_folder='assets')
app.config['SECRET_KEY'] = 'key goes here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

#db setup
db = SQLAlchemy()
db.init_app(app)

#login stuff
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models import User
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg', '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX', 'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']
datatypes = {'audio': 'm4a,mp3,oga,ogg,webma,wav', 'archive': '7z,zip,rar,gz,tar', 'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'pdf': 'pdf', 'quicktime': '3g2,3gp,3gp2,3gpp,mov,qt', 'source': 'atom,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml,plist', 'text': 'txt', 'video': 'mp4,m4v,ogv,webm,MP4', 'website': 'htm,html,mhtm,mhtml,xhtm,xhtml'}
icontypes = {'fa-music': 'm4a,mp3,oga,ogg,webma,wav', 'fa-archive': '7z,zip,rar,gz,tar', 'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'fa-file-text': 'pdf', 'fa-film': '3g2,3gp,3gp2,3gpp,mov,qt', 'fa-code': 'atom,plist,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml', 'fa-file-text-o': 'txt', 'fa-film': 'mp4,m4v,ogv,webm,MP4', 'fa-globe': 'htm,html,mhtm,mhtml,xhtm,xhtml'}


@login_manager.user_loader
def load_user(user_id):
    return(User.query.get(int(user_id)))


def get_user_root():
    #current_user is imported from flask_login
    uroot = os.path.join(root, str(current_user.id))
    return(uroot)


# template_filter is used to make a jinja template
@app.template_filter('size_fmt')
def size_fmt(size):
    return humanize.naturalsize(size)


@app.template_filter('time_fmt')
def time_desc(timestamp):
    mdate = datetime.fromtimestamp(timestamp)
    str = mdate.strftime('%Y-%m-%d %H:%M:%S')
    return str


@app.template_filter('data_fmt')
def data_fmt(filename):
    t = 'unknown'
    for type, exts in datatypes.items():
        if filename.split('.')[-1] in exts:
            t = type
    return t


@app.template_filter('icon_fmt')
def icon_fmt(filename):
    i = 'fa-file-o'
    for icon, exts in icontypes.items():
        if filename.split('.')[-1] in exts:
            i = icon
    return i


@app.template_filter('humanize')
def time_humanize(timestamp):
    mdate = datetime.fromtimestamp(timestamp)
    return humanize.naturaltime(mdate)


def get_root_usage():
    out = sub.check_output('df | awk \'/\/dev\/root/ {print $5}\'', shell=1)
    out = out.decode('utf-8').strip()
    print(out)


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        type = 'dir'
    else:
        type = 'file'
    return type


def streaming_response(path, start, end=None):
    def make_response_chunk(path, start, chunk_size, length):
        print("start: {}, chunk_size: {}, length: {}".format(
            start, chunk_size, length))
        iters = length // chunk_size
        for i in range(iters):
            with open(path, 'rb') as fd:
                fd.seek(start)
                bytes_read = fd.read(chunk_size)
            errmsg = "Chunk size: {}, bytes read: {}".format(
                chunk_size,
                len(bytes_read))
            assert len(bytes_read) == chunk_size, errmsg
            print("Yielding {} bytes".format(chunk_size))
            yield bytes_read
            start += chunk_size
        remainder = length-chunk_size*iters
        if remainder > 0:
            with open(path, 'rb') as fd:
                fd.seek(start)
                bytes_read = fd.read(remainder)
            errmsg = "Remainder bytes: {}, bytes read: {}".format(
                remainder,
                len(bytes_read))
            #assert len(bytes_read) == remainder, errmsg
            print("Yielding a remainder of {} bytes".format(
                len(bytes_read)))
            yield bytes_read

    file_size = os.path.getsize(path)
    if (start > file_size-1) or (end < start):
        #Request not satisfiable
        response = Response(416)
        return(response)

    if end is None:
        length = file_size-start
    else:
        length = end-start+1

    chunk_size = 1 << 20 #one megabyte
    #chunk_size = 1 << 17

    response = Response(
        stream_with_context(
            make_response_chunk(path, start, chunk_size,
                length
            )
        ),
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, start+length, file_size-1
        ),
    )
    response.headers.add(
        'Content-Length', length
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return(response)


def partial_response(path, start, end=None, max_length=None):
    file_size = os.path.getsize(path)
    if end is None:
        end = file_size-1
    if (start > file_size-1) or (end < start):
        #Request not satisfiable
        response = Response(416)
        return(response)
    length = end-start+1

    #max length functionality
    if max_length and length > max_length:
        length = max_length

    print("file size: {}, start: {}, length: {}".format(
        file_size, start, length))

    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, start+length, file_size-1,
        )
    )
    response.headers.add(
        'Content-Length', length
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response


def get_range(request):
    request_range = request.headers.get('Range', None)
    print("get range finds: {}".format(request_range))
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', request_range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None


class PathView(MethodView):
    @login_required
    def get(self, p=''):
        hide_dotfile = request.args.get('hide-dotfile', request.cookies.get('hide-dotfile', 'no'))
        path = os.path.join(get_user_root(), p)
        if os.path.isdir(path):
            contents = []
            total = {'size': 0, 'dir': 0, 'file': 0}
            for filename in os.listdir(path):
                if filename in ignored:
                    continue
                if hide_dotfile == 'yes' and filename[0] == '.':
                    continue
                filepath = os.path.join(path, filename)
                stat_res = os.stat(filepath)
                info = {}
                info['name'] = filename
                info['mtime'] = stat_res.st_mtime
                ft = get_type(stat_res.st_mode)
                info['type'] = ft
                total[ft] += 1
                sz = stat_res.st_size
                info['size'] = sz
                total['size'] += sz
                contents.append(info)
            page = render_template('index.html', path=p, contents=contents, total=total, hide_dotfile=hide_dotfile)
            res = make_response(page, 200)
            res.set_cookie('hide-dotfile', hide_dotfile, max_age=16070400)
        elif os.path.isfile(path):
            if 'Range' in request.headers:
                start, end = get_range(request)
                res = partial_response(path, start, end, max_length=5*(1<<20))
                #res = streaming_response(path, start, end)
            else:
                print('No range specified in header')
                res = send_file(path)
                res.headers.add('Content-Disposition', 'attachment')
        else:
            res = make_response('Not found', 404)
        return res
    
    @login_required
    def put(self, p=''):
        path = os.path.join(get_user_root(), p)
        dir_path = os.path.dirname(path)
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        info = {}
        if os.path.isdir(dir_path):
            try:
                filename = secure_filename(os.path.basename(path))
                with open(os.path.join(dir_path, filename), 'wb') as f:
                    f.write(request.stream.read())
            except Exception as e:
                info['status'] = 'error'
                info['msg'] = str(e)
            else:
                info['status'] = 'success'
                info['msg'] = 'File Saved'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
        res = make_response(json.JSONEncoder().encode(info), 201)
        res.headers.add('Content-type', 'application/json')
        return res

    @login_required
    def post(self, p=''):
        path = os.path.join(get_user_root(), p)
        Path(path).mkdir(parents=True, exist_ok=True)

        info = {}
        if os.path.isdir(path):
            files = request.files.getlist('files[]')
            for file in files:
                try:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(path, filename))
                except Exception as e:
                    info['status'] = 'error'
                    info['msg'] = str(e)
                else:
                    info['status'] = 'success'
                    info['msg'] = 'File Saved'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
        res = make_response(json.JSONEncoder().encode(info), 200)
        res.headers.add('Content-type', 'application/json')
        return res

    @login_required   
    def delete(self, p=''):
        path = os.path.join(get_user_root(), p)
        dir_path = os.path.dirname(path)
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        info = {}
        if os.path.isdir(dir_path):
            try:
                filename = secure_filename(os.path.basename(path))
                os.remove(os.path.join(dir_path, filename))
                os.rmdir(dir_path)
            except Exception as e:
                info['status'] = 'error'
                info['msg'] = str(e)
            else:
                info['status'] = 'success'
                info['msg'] = 'File Deleted'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
        res = make_response(json.JSONEncoder().encode(info), 204)
        res.headers.add('Content-type', 'application/json')
        return res

path_view = PathView.as_view('path_view')
app.add_url_rule('/', view_func=path_view)
app.add_url_rule('/<path:p>', view_func=path_view)
