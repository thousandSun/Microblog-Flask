from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required  # makes the page protected
def index():
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
        # loads user from database using the inputted username
        user = User.query.filter_by(username=form.username.data).first()
        # checks to see if a user is registered, and if the password matches
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # makes it so that any other pages the user visits, they're still logged in
        login_user(user, remember=form.remember_me.data)
        # following 4 lines are needed to return user to page that requires login
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    # create user and write them to the database then redirects to index
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, you\'re registered')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


# <username> is dynamic, whatever is passed here will be used as the parameter for the view function
# to pass data into it, access by keyword argument e.g. username='susan'
@app.route('/user/<username>')
@login_required
def user(username):
    # first_or_404() will either return a user object or a 404 html error message
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'test post #1'},
        {'author': user, 'body': 'test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.before_request  # allows this function to be ran prior to the view function
def before_request():
    """sets the users last seen time prior to fulfilling a request"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Changed have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
