#!flask/bin/python

import os
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
from common.kb.dbpedia import DBpedia
from common.utility.utils import Utils
from common.utility.cacheDict import CacheDict
from common.utility.reverseProxied import ReverseProxied
from database.tabledef import User, InteractionLog, AnsweredQuestion

app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/IQA.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

global sparql2nl_cache
global LoginForm
global kb


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
    session['start'] = datetime.datetime.utcnow()
    log_interaction()

    return render_template('survey.html', data=result)


@app.route('/interact', methods=['POST'])
@login_required
def interact():
    data = {'userid': current_user.username, 'answer': flask.request.values['answer']}

    log_interaction(interaction=jsonify(session['current_IO']).data, answer=data['answer'])

    result = Utils.call_web_api('http://127.0.0.1:5002/iqa/ui/v1.0/interact', data)
    return jsonify(reformat(result))


def reformat(result):
    if result is not None:
        if 'stats' in result:
            result['stats'] = {'progress': (100.0 * result['stats']['answered'] / result['stats']['total'])}
        if 'command' in result:
            if result['command'] == 'next_question':
                mark_as_answered()
            pass
        else:
            if 'qid' in result and result['qid'] is not None:
                session['question_id'] = result['qid']
            if 'IO' in result:
                session['current_IO'] = result['IO']
            if 'query' in result:
                session['current_query'] = result['query']

            result['sparql2nl'] = sparql2nl(result['query'])
            if 'IO' in result:
                if len(result['IO']['values']) == 0:
                    result['IO']['surface'] = 'Is it what the question means?'
                    result['IO']['values'] = [{'label': result['sparql2nl'], 'abstract': ''}]
                else:
                    if result['IO']['surface'] == 'question_type':
                        result['IO']['surface'] = 'Is the type of question ...?'
                        result['IO']['values'][0] = {'label': result['IO']['values'][0], 'abstract': ''}
                    else:
                        result['IO']['surface'] = 'Does "{0}" refers to ...?'.format(result['IO']['surface'])
                        for idx in range(len(result['IO']['values'])):
                            val = result['IO']['values'][idx]
                            if 'dbpedia.org' in val:
                                label, abstract = kb.get_label_abstract(val)
                                description = kb.get_wikidata_description(val)
                                raw_example_triples = kb.get_example_triples(val)
                                example_triples = []
                                for i in range(len(raw_example_triples)):
                                    example_triples.append(Utils.triple_to_nl(raw_example_triples[i][0],
                                                                              val,
                                                                              raw_example_triples[i][1]))
                                result['IO']['values'][idx] = {'label': label,
                                                               'abstract': abstract,
                                                               'description': description,
                                                               'example_triples': example_triples}

    return result


@app.route('/correct')
@login_required
def correct():
    log_interaction(data='early_correct')
    mark_as_answered()
    return redirect('survey')


@app.route('/skip')
@login_required
def skip():
    reason = 'skip'
    if 'reason' in flask.request.values:
        reason = flask.request.values['reason']

    log_interaction(data='skip:' + reason)
    mark_as_answered(data='skip:' + reason)
    return redirect('survey')


def sparql2nl(query):
    global sparql2nl_cache
    try:
        if query is None:
            return 'No Query'
        if query in sparql2nl_cache:
            return sparql2nl_cache[query]
        if 'ASK ' in query:
            return query

        req = requests.get('https://aifb-ls3-kos.aifb.kit.edu/projects/spartiqulator/v5/verbalize.pl',
                           params={'sparql': query})
        raw_output = req.text
        idx_start = raw_output.index('verbalization"><b>') + len('verbalization"><b>')
        idx_end = raw_output.index('</b>', idx_start)
        output = raw_output[idx_start:idx_end]
        sparql2nl_cache[query] = output
        return output
    except:
        return query


def log_interaction(interaction='', answer='', data=''):
    log_record = InteractionLog(current_user.username,
                                session['question_id'],
                                session['session_id'],
                                interaction,
                                answer,
                                session['current_query'],
                                datetime.datetime.utcnow(),
                                data)
    db.session.add(log_record)
    db.session.commit()


def mark_as_answered(data=None):
    now = datetime.datetime.utcnow()
    record = AnsweredQuestion(current_user.username,
                              session['question_id'],
                              '',
                              now,
                              (now - session['start']).total_seconds(),
                              data)
    db.session.add(record)
    db.session.commit()


if __name__ == '__main__':
    global sparql2nl_cache
    global kb
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    parser.add_argument("--base_path", help="base path", default="../", dest="base_path")
    args = parser.parse_args()
    logger.info(args)

    sparql2nl_cache = CacheDict(os.path.join(args.base_path, 'caches', 'sparql2nl.cache'))
    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)

    app.run(debug=True, port=args.port)
