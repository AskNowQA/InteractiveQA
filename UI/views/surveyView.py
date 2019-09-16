import datetime

import ujson as json
import flask
from flask_login import login_required, current_user
from flask_classful import FlaskView, route

from UI.database.tabledef import InteractionLog, AnsweredQuestion
from common.utility.utils import Utils
from config import config


class SurveyView(FlaskView):
    decorators = [login_required]
    db = None
    kb = None

    def index(self):
        data = {'userid': current_user.username}
        if 'qid' in flask.request.values:
            data['qid'] = flask.request.values['qid']
        if 'strategy' in flask.request.values:
            data['strategy'] = flask.request.values['strategy']

        result = Utils.call_web_api(config['IQA']['backend'] + '/survey/start', data)
        if result is None:
            return flask.render_template('error.html', data={'message': 'Backend is not accessible'})

        result = self.reformat(result)

        # Log the record
        flask.session['session_id'] = Utils.rand_id()
        flask.session['start'] = datetime.datetime.utcnow()
        if 'command' not in result or result['command'] != 'end_survey':
            self.log_interaction()

        return flask.render_template('survey.html', data=result)

    @route('interact', methods=['POST'])
    def interact(self):
        data = {'userid': current_user.username, 'answer': flask.request.values['answer']}

        self.log_interaction(interaction=flask.jsonify(flask.session['current_IO']).data, answer=data['answer'])

        result = Utils.call_web_api(config['IQA']['backend'] + '/survey/interact', data)
        return flask.jsonify(self.reformat(result))

    @route('feedback', methods=['POST'])
    def feedback(self):
        if not flask.request.values:
            flask.abort(400)
        self.log_interaction(interaction='feedback',
                             data=json.dumps({'r1': flask.request.values['r1'],
                                              'r2': flask.request.values['r2'],
                                              'comment': flask.request.values['comment']}))
        return flask.make_response(flask.jsonify({}), 200)

    def correct(self):
        self.log_interaction(data='early_correct')
        self.mark_as_answered(final_query=flask.session['current_query'])
        return flask.redirect(flask.url_for('SurveyView:index'))

    def skip(self):
        reason = 'skip'
        if 'reason' in flask.request.values:
            reason = flask.request.values['reason']

        self.log_interaction(data='skip:' + reason)
        self.mark_as_answered(data='skip:' + reason)
        return flask.redirect(flask.url_for('SurveyView:index'))

    def reformat(self, result):
        if result is not None:
            if 'stats' in result:
                result['stats'] = {'progress': "{0:.2f}".format(100.0 * result['stats']['answered'] / result['stats']['total'])}
            else:
                result['stats'] = {'progress': 0}

            if 'qid' in result and result['qid'] is not None:
                flask.session['question_id'] = result['qid']
            if 'IO' in result:
                flask.session['current_IO'] = result['IO']
                if 'surface' in result['IO'] and result['IO']['surface'] == 'question_type':
                    if result['IO']['values'][0] == 'list':
                        result['IO']['values'][0] = 'Single or multiple item(s)'
                    elif result['IO']['values'][0] == 'list':
                        result['IO']['values'][0] = 'Number of some items'
                    elif result['IO']['values'][0] == 'boolean':
                        result['IO']['values'][0] = 'Yes or No'
            if 'query' in result and result['query'] is not None:
                flask.session['current_query'] = result['query']
                result['query'] = result['query'].replace('{', '{\n').replace('}', '\n}').replace(' .', ' .\n')

            if 'command' in result:
                if result['command'] == 'next_question':
                    self.mark_as_answered(final_query=flask.session['current_query'])
                pass
            elif 'query' in result:
                result['sparql2nl'] = Utils.sparql2nl(result['query'])
                if 'IO' in result:
                    if len(result['IO']['values']) == 0:
                        result['IO']['surface'] = 'Is it what the question means?'
                        result['IO']['values'] = [{'label': result['sparql2nl'], 'abstract': ''}]
                    else:
                        if result['IO']['surface'] == 'question_type':
                            result['IO']['surface'] = 'Is the expected answer(s) ...?'
                            result['IO']['values'][0] = {'label': result['IO']['values'][0], 'abstract': ''}
                        else:
                            if len(result['IO']['surface']) == 0:
                                result['IO']['surface'] = 'Does any part of the question refers to ...?'
                            else:
                                result['IO']['surface'] = 'Does "{0}" refers to ...?'.format(result['IO']['surface'])
                            for idx in range(len(result['IO']['values'])):
                                val = result['IO']['values'][idx]
                                if 'dbpedia.org' in val:
                                    label, abstract = self.kb.get_label_abstract(val)
                                    description = self.kb.get_wikidata_description(val)
                                    raw_example_triples = self.kb.get_example_triples(val)
                                    example_triples = []
                                    for i in range(len(raw_example_triples)):
                                        example_triples.append(Utils.triple2nl(raw_example_triples[i][0],
                                                                               val,
                                                                               raw_example_triples[i][1]))
                                    result['IO']['values'][idx] = {'label': label,
                                                                   'abstract': abstract,
                                                                   'description': description,
                                                                   'example_triples': example_triples}

        return result

    def log_interaction(self, interaction='', answer='', data=''):
        log_record = InteractionLog(current_user.username,
                                    flask.session['question_id'],
                                    flask.session['session_id'],
                                    interaction,
                                    answer,
                                    flask.session['current_query'],
                                    datetime.datetime.utcnow(),
                                    data)
        self.db.session.add(log_record)
        self.db.session.commit()

    def mark_as_answered(self, data=None, final_query=None):
        now = datetime.datetime.utcnow()
        record = AnsweredQuestion(current_user.username,
                                  flask.session['question_id'],
                                  '',
                                  now,
                                  (now - flask.session['start']).total_seconds(),
                                  data,
                                  final_query)
        self.db.session.add(record)
        self.db.session.commit()
