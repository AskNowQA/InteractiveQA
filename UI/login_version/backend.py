#!flask/bin/python
import sys
import os

module_path = os.path.abspath(os.path.join('/Users/liuhaohui/Documents/GitHub/InteractiveQA/UI/login_version/templates/index.html'))
if module_path not in sys.path:
    sys.path.append(module_path)

import flask
import argparse
import logging
import json
from common.utility.utils import Utils
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import jsonify

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/liuhaohui/Desktop/building_user_login_system-master/finish/database.db '
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


@app.route('/iqa/ui/v1.0/start', methods=['POST'])
def start():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']

    result = {'question': 'Name the municipality of Robert Clemente Bridge?',
              'IO': {'surface': 'Robert Clemente Bridge',
                     'values': ['Robert Clemente Bridge', 'Robert Clemente Community School']}}

    return json.dumps(result)


@app.route('/iqa/ui/v1.0/interact', methods=['POST'])
def interact():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']
    io = flask.request.json['IO']
    result = {'IO': {'surface': 'municipality',
                     'values': ['municipality', 'city']}}

    return json.dumps(result)

@app.route('/mystringa')
def start1():
    #if not flask.request.json:
     #   flask.abort(400)

    #userid = flask.request.json['userid']

    result = {'question': 'Name the municipality of Robert Clemente Bridge?',
              'IO': {'surface': 'Robert Clemente Bridge',
                     'values': ['Robert Clemente Bridge', 'Robert Clemente Community School']}}

    #data = json.dumps(result)
    #return json.dumps(result)
    return jsonify(result)

@app.route('/mystringc')
def interact1():
 
    #userid = flask.request.json['userid']
    #io = flask.request.json['IO']
    result = {'IO': {'surface': 'municipality',
                     'values': ['municipality', 'city']}}

    return jsonify(result)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    app.run(debug=True, port=args.port)