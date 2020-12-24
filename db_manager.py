#!/usr/bin/env python3


from file_server import db, app
from models import User
import argparse, os


def func_in_context(app, func, **kwargs):
    #gets a context before executing a function
    with app.app_context():
        user = User.query.filter_by(**kwargs).first()
        func(user)


if __name__ == '__main__':
    '''
    Utility for adding new users to the database.
    '''
    parser = argparse.ArgumentParser(allow_abbrev=True)
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
    parser.add_argument('-r', '--rootdir',
        action='store',
        type=str,
        default='server-root',
        help='Root directory of file server (default ./server-root)')

    args = parser.parse_args()

    init = args.init
    approve = args.approve
    uname = args.uname
    email = args.email
    approve = args.approve
    disapprove = args.disapprove
    info = args.info
    rootdir = args.rootdir

    if init:
        print("Writing new database")
        db.create_all(app=app)

    kwargs = None
    if email:
        kwargs = {'email': email}
    elif uname:
        kwargs = {'name': uname}

    if kwargs:
        if approve: 
            def approve_func(user):
                user.approved = True
                db.session.commit()
                uid = user.id
                userdir = os.path.join(rootdir, str(uid))
                os.mkdir(userdir)
            func_in_context(app, approve_func, **kwargs)
        elif disapprove:
            def disapprove_func(user):
                user.approved = False
                db.session.commit()
            func_in_context(app, disapprove_func, **kwargs)
        if info:
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
            func_in_context(app, info_func, **kwargs)
