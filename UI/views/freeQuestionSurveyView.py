import flask
from flask_login import login_required, current_user
from flask.ext.classy import FlaskView, route

from UI.forms.submitQuestionForm import SubmitQuestionForm
from common.utility.utils import Utils
from config import config


class FreeQuestionSurveyView(FlaskView):
    decorators = [login_required]
    kb = None

    @route('index', methods=['GET', 'POST'])
    def index(self):
        result = {'content_visibility': 'hidden'}
        form = SubmitQuestionForm()
        if form.validate_on_submit():
            data = {'userid': current_user.username}
            if 'strategy' in flask.request.values:
                data['strategy'] = flask.request.values['strategy']
            data['question'] = form.question.data

            result = Utils.call_web_api(config['IQA']['backend'] + '/freequestionsurvey/index', data)
            # Log the record
            # session['session_id'] = Utils.rand_id()
            # session['start'] = datetime.datetime.utcnow()
            # if 'command' not in result or result['command'] != 'end_survey':
            #     log_interaction()

            result['content_visibility'] = 'visible'
        result = self.reformat(result)
        return flask.render_template('surveyFreeQuestion.html', data=result, form=form)

    @route('interact', methods=['POST'])
    def interact(self):
        data = {'userid': current_user.username, 'answer': flask.request.values['answer']}

        # log_interaction(interaction=flask.jsonify(session['current_IO']).data, answer=data['answer'])

        result = Utils.call_web_api(config['IQA']['backend'] + '/interact', data)
        return flask.jsonify(self.reformat(result))

    def correct(self):
        # log_interaction(data='early_correct')
        # mark_as_answered(final_query=flask.session['current_query'])
        return flask.redirect('survey')

    def skip(self):
        reason = 'skip'
        if 'reason' in flask.request.values:
            reason = flask.request.values['reason']

        # log_interaction(data='skip:' + reason)
        # mark_as_answered(data='skip:' + reason)
        return flask.redirect('survey')

    def reformat(self, result):
        if result is not None:
            if 'stats' in result:
                result['stats'] = {'progress': (100.0 * result['stats']['answered'] / result['stats']['total'])}
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
            if 'query' in result:
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
