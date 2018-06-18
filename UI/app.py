#!flask/bin/python


import argparse
import logging
import flask
from flask_bootstrap import Bootstrap
from flask import Flask, flash, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

from forms.loginForm import LoginForm
from forms.registerForm import RegisterForm
from common.utility.utils import Utils
from database.tabledef import User

from common.utility.utils import Utils

app = flask.Flask(__name__)
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
        flash('Invalid username or password')

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
    result = Utils.call_web_api('http://127.0.0.1:5002/iqa/ui/v1.0/start', {'userid': current_user.username})
    result['sparql2nl'] = sparql2nl(result['query'])
    return render_template('survey.html', data=result)


@app.route('/interact', methods=['POST'])
@login_required
def interact():
    data = {'userid': current_user.username, 'answer': flask.request.values['answer']}
    result = Utils.call_web_api('http://127.0.0.1:5002/iqa/ui/v1.0/interact', data)
    result['sparql2nl'] = sparql2nl(result['query'])
    return jsonify(result)


def sparql2nl(query):
    raw_output = Utils.call_web_api(
        'https://aifb-ls3-kos.aifb.kit.edu/projects/spartiqulator/v5/verbalize.pl',
        raw_input={'sparql': query},
        use_json=False, use_url_encode=True, parse_response_json=False)
    idx_start = raw_output.index('verbalization"><b>') + len('verbalization"><b>')
    idx_end = raw_output.index('</b>', idx_start)
    return raw_output[idx_start:idx_end]


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    app.run(debug=True, port=args.port)