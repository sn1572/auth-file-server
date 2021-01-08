#!/usr/bin/env python3


from file_server import db, app
from models import User
from werkzeug.security import generate_password_hash
import argparse, os


'''
decorators
'''
def in_context(f):
    #Like it says on the tin. This decorator probably
    #exists in the imports somewhere.
    global app
    def wrapper(*args, **kwargs):
        with app.app_context():
            f(*args, **kwargs)
    return(wrapper)


def exit_after(f):
    #Simplest way to ensure only one function
    #of the decorated type ever executes. #lazy
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        exit()
    return(wrapper)


'''
functionality
'''
@in_context
def users_lambda(f, **user_descr):
    #Selects every user meeting the criteria in
    #user_descr and applies the function f to each.
    users = User.query.filter_by(**user_descr)
    if not users:
        print('No users found meeting any of the following criteria:')
        for key, val in kwargs.items():
            print('{}: {}'.format(key, val))
    for user in users:
        f(user)


def approve_func(user):
    user.approved = True
    db.session.commit()
    uid = user.id
    userdir = os.path.join(rootdir, str(uid))
    if not os.path.isdir(userdir):
        os.mkdir(userdir)


def disapprove_func(user):
    user.approved = False
    db.session.commit()


def info_func(user):
    name = user.name
    email = user.email
    approved = user.approved
    uid = user.id
    print('\033[1mUser info\033[0m')
    print("{:>12}: {}\n{:>12}: {}\n{:>12}: {}\n{:>12}: {}".\
        format('name', name, 'e-mail',
            email, 'approved', approved,
            'id', uid))


@in_context
@exit_after
def list_all_func():
    users = User.query.all()
    for user in users:
        info_func(user)


@exit_after
def init_func():
    print("Writing new database")
    db.create_all(app=app)
    if not os.path.isdir(rootdir):
        print("Creating server root dir at {}".format(
            rootdir))
        os.mkdir(rootdir)


@in_context
def reset_password(password, **user_descr):
    user = User.query.filter_by(**user_descr).first()
    if not user:
        print('No users found meeting any of the following criteria:')
        for key, val in kwargs.items():
            print('{}: {}'.format(key, val))
    user.password = generate_password_hash(password, method='sha256')
    db.session.commit()


if __name__ == '__main__':
    descr = '''
    Utility for interacting with the database.
    Common use case is approval. Use -u -e -i to identify
    a user and -a (-d) to approve (disapprove).
    Example: ./db_manager.py -e you@mail.com -a
    '''
    parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=descr)
    parser.add_argument('--init', 
        action='store_true',
        help='Creates a new database if one does not exist.')
    parser.add_argument('-a', '--approve',
        action='store_true',
        help='Given a uname or email, sets approve flag for the user.')
    parser.add_argument('-d', '--disapprove',
        action='store_true',
        help='Given a uname or email, set disapprove flag for the user.')
    parser.add_argument('--info',
        action='store_true',
        help='Given a uname or email, prints variables for the user.')
    parser.add_argument('-u', '--uname',
        action='store',
        type=str,
        help='User name of account to modify.')
    parser.add_argument('-e', '--email',
        action='store',
        type=str,
        help='User email of account to modify.')
    parser.add_argument('-i', '--id',
        action='store',
        type=str,
        help='User id of account to modify.')
    parser.add_argument('-r', '--rootdir',
        action='store',
        type=str,
        default='server-root',
        help='''Root directory of file server (default ./server-root).
            Argument required if approving a user or initializing with
            a custom root directory.''')
    parser.add_argument('-l', '--list',
        action = 'store_true',
        help="List all users in the database")
    parser.add_argument('-p', '--password',
        action = 'store',
        type=str,
        help="Enter a new password for the user.")

    args = parser.parse_args()

    init = args.init
    approve = args.approve
    uname = args.uname
    email = args.email
    approve = args.approve
    disapprove = args.disapprove
    info = args.info
    rootdir = args.rootdir
    listall = args.list
    uid = args.id
    password = args.password

    '''
    Functions that don't need a user or users
    to be specified.
    '''
    if init:
        init_func()

    if listall:
        list_all_func()

    '''
    This block gets the specified user.
    Multi-user specification is possible
    with the User.query library, but not yet
    implemented.
    TODO implement multi-user specification
    with a decorator to promote f(user)
    to f(list(user))
    '''
    user_descr = None
    if email:
        user_descr = {'email': email}
    elif uname:
        user_descr = {'name': uname}
    elif uid:
        user_descr = {'id': uid}
    if not user_descr:
        print("No user identifier specified. Use -e, -u, or -i flags.")
        exit()

    '''
    Implement logic for prioritizing cli flag
    execution here.
    '''
    if approve: 
        users_lambda(approve_func, **user_descr)
    elif disapprove:
        users_lambda(disapprove_func, **user_descr)

    if info:
        users_lambda(info_func, **user_descr)

    if password:
        reset_password(password, **user_descr)
