#!flask/bin/python

import datetime
import argparse
import logging
import requests
import flask
from flask_bootstrap import Bootstrap
from flask import Flask, flash, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

from forms.loginForm import LoginForm
from forms.registerForm import RegisterForm
from common.utility.utils import Utils
from database.tabledef import User, InteractionLog


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)


app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/IQA.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

global LoginForm


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
        flash('Error: Invalid username or password')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('New user has been created!')

    return render_template('signup.html', form=form)


@app.route('/survey')
@login_required
def survey():
    data = {'userid': current_user.username}
    if 'qid' in flask.request.values:
        data['qid'] = flask.request.values['qid']
    if 'strategy' in flask.request.values:
        data['strategy'] = flask.request.values['strategy']

    result = Utils.call_web_api('http://127.0.0.1:5002/iqa/ui/v1.0/start', data)
    result = reformat(result)

    # Log the record
    session['session_id'] = Utils.rand_id()
    log_record = InteractionLog(current_user.username,
                                session['question_id'],
                                session['session_id'],
                                '',
                                '',
                                session['current_query'],
                                datetime.datetime.utcnow())
    db.session.add(log_record)
    db.session.commit()

    return render_template('survey.html', data=result)


@app.route('/interact', methods=['POST'])
@login_required
def interact():
    data = {'userid': current_user.username, 'answer': flask.request.values['answer']}

    log_record = InteractionLog(current_user.username,
                                session['question_id'],
                                session['session_id'],
                                jsonify(session['current_IO']).data,
                                data['answer'],
                                session['current_query'],
                                datetime.datetime.utcnow())
    db.session.add(log_record)
    db.session.commit()

    result = Utils.call_web_api('http://127.0.0.1:5002/iqa/ui/v1.0/interact', data)
    return jsonify(reformat(result))


def reformat(result):
    if result is not None:
        if 'command' in result:
            pass
        else:
            if 'qid' in result and result['qid'] is not None:
                session['question_id'] = result['qid']
            if 'IO' in result:
                session['current_IO'] = result['IO']
            if 'query' in result:
                session['current_query'] = result['query']

            result['sparql2nl'] = sparql2nl(result['query'])
            if 'IO' in result and len(result['IO']['values']) == 0:
                result['IO']['surface'] = result['sparql2nl']
                result['IO']['values'] = ['Correct?']

    return result


@app.route('/correct')
@login_required
def correct():
    return redirect('survey')


@app.route('/skip')
@login_required
def skip():
    return redirect('survey')


def sparql2nl(query):
    try:
        if query is None:
            return 'No Query'

        req = requests.get('https://aifb-ls3-kos.aifb.kit.edu/projects/spartiqulator/v5/verbalize.pl',
                           params={'sparql': query})
        raw_output = req.text
        idx_start = raw_output.index('verbalization"><b>') + len('verbalization"><b>')
        idx_end = raw_output.index('</b>', idx_start)
        return raw_output[idx_start:idx_end]
    except:
        return query


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    app.run(debug=True, port=args.port)
