from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from file_server import db
from flask_login import login_user, login_required, current_user, logout_user
from stats import reports, net_usage_pie, net_usage_bar
import os


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return(render_template('login.html'))


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    # have they been approved?
    if not user.approved:
        flash('User awaiting admin approval to join.')
        return(redirect(url_for('auth.login')))

    # if the above checks pass, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('auth.profile'))


@auth.route('/signup')
def signup():
    return(render_template('signup.html'))


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user: # if a user is found, we want to redirect back to signup page
        flash('Email address already exists')
        return(redirect(url_for('auth.signup')))

    # create a new user with the form data.
    new_user = User(email=email,
        name=name,
        password=generate_password_hash(password, method='sha256'),
        approved=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return(redirect(url_for('auth.login')))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return(redirect(url_for('path_view')))


@auth.route('/profile')
@login_required
def profile():
    return(render_template('profile.html', name=current_user.name))


@auth.route('/about')
def about():
    net_usage_pie()
    net_usage_bar()
    imgs = os.listdir(os.path.join('assets', 'abt-img'))
    imgs = list(map(lambda fname: os.path.join('abt-img', fname), imgs))
    print(imgs)
    return(render_template('about.html', reports=reports, imgs=imgs))
