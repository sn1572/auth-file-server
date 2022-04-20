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

ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg',
           '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX',
           'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']
datatypes = {'audio': 'm4a,mp3,oga,ogg,webma,wav',
             'archive': '7z,zip,rar,gz,tar',
             'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'pdf': 'pdf',
             'quicktime': '3g2,3gp,3gp2,3gpp,mov,qt',
             'source': ('atom,bat,bash,c,cmd,coffee,css,hml,js,json,java,'
                        'less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,'
                        'scss,sh,xml,yml,plist'),
             'text': 'txt', 'video': 'mp4,m4v,ogv,webm,MP4',
             'website': 'htm,html,mhtm,mhtml,xhtm,xhtml'}
icontypes = {'fa-music': 'm4a,mp3,oga,ogg,webma,wav',
             'fa-archive': '7z,zip,rar,gz,tar',
             'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp',
             'fa-file-text': 'pdf', 'fa-film': '3g2,3gp,3gp2,3gpp,mov,qt',
             'fa-code': ('atom,plist,bat,bash,c,cmd,coffee,css,hml,js,json,'
                         'java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,'
                         'swift,scss,sh,xml,yml'),
             'fa-file-text-o': 'txt', 'fa-film': 'mp4,m4v,ogv,webm,MP4',
             'fa-globe': 'htm,html,mhtm,mhtml,xhtm,xhtml'}


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
    for file_type, extension in datatypes.items():
        if filename.split('.')[-1] in extension:
            t = file_type
            break
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


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        mode_type = 'dir'
    else:
        mode_type = 'file'
    return mode_type


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
        data = fd.read(length)
    assert len(data) == length

    print(f'Mimetype: {mimetypes.guess_type(path)[0]}')
    response = Response(
        data,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', f'bytes {start}-{start+length-1}/{file_size}'
    )
    response.headers.add(
        'Content-Length', f'{length}'
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


def get_info(filepath):
    stat_res = os.stat(filepath)
    info = {}
    info['name'] = os.path.basename(filepath)
    info['mtime'] = stat_res.st_mtime
    ft = get_type(stat_res.st_mode)
    info['type'] = ft
    sz = stat_res.st_size
    info['size'] = sz
    info['extension'] = (os.path.splitext(filepath)[1])[1:]
    return info


class PathView(MethodView):
    @login_required
    def get(self, p=''):
        hide_dotfile = request.args.get('hide-dotfile',
                                        request.cookies.get('hide-dotfile',
                                                            'no'))
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
                info = get_info(filepath)
                total[info['type']] += 1
                total['size'] += info['size']
                contents.append(info)
            page = render_template('index.html', path=p, contents=contents,
                                   total=total, hide_dotfile=hide_dotfile)
            res = make_response(page, 200)
            res.set_cookie('hide-dotfile', hide_dotfile, max_age=16070400)
        elif os.path.isfile(path):
            if 'Range' in request.headers:
                start, end = get_range(request)
                chunk_size = 5*(1<<20)
                res = partial_response(path, start, end,
                                       max_length=chunk_size)
            else:
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
