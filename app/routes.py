from app import app
from app.forms import LoginForm
from app.models import User
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required  # makes the page protected
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # this deals with user that is already logged in
    # trying to navigate to the login page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # validates field data using validators provided in the form class
    # returns true if everything checks out, false if something is missing
    if form.validate_on_submit():
        # loads user from database
        user = User.query.filter_by(username=form.username.data).first()
        # checks to see if a user is registered, and if the password matches
        if user is None or user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # makes it so that any other pages the user visits, theyre still logged in
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """logs user out that is currently logged in"""
    logout_user()
    return redirect(url_for('index'))
