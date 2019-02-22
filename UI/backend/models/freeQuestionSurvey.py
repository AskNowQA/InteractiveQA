import os
import time

import flask
from flask_login import login_required, current_user
from flask_classful import FlaskView, route

from common.container.qapair import QApair
from common.pipeline import IQAPipeline
from common.interaction.interactionManager import InteractionManager
from common.utility.utils import Utils
from config import config


class FreeQuestionSurvey(FlaskView):
    route_base = 'freequestionsurvey'
    interaction_types = [[False, True], [True, True]]
    pipeline_data = dict()
    interaction_data = dict()
    interaction_history = []
    book_keeper = None
    parser = None
    pipeline = None
    kb = None
    args = None
    strategy = None

    @route('new_task', methods=['POST'])
    def new_task(self):
        if not flask.request.json:
            flask.abort(400)

        userid = flask.request.json['userid']
        question, query, io = '', None, None
        question_id, task, total, answered = FreeQuestionSurvey.book_keeper.new_task(userid)
        output = self.handle_IO(question, question_id, query, io)
        output['task'] = task
        output['stats'] = {'total': total, 'answered': answered}
        return flask.jsonify(output)

    @route('start_task', methods=['POST'])
    def start_task(self):
        if FreeQuestionSurvey.pipeline is None:
            FreeQuestionSurvey.pipeline = IQAPipeline(self.args, self.kb, self.parser.parse_sparql)
        if not flask.request.json:
            flask.abort(400)

        userid = flask.request.json['userid']
        if 'strategy' in flask.request.json:
            if flask.request.json['strategy'] in ['InformationGain', 'OptionGain', 'Probability']:
                self.strategy = flask.request.json['strategy']
        question, query, io = '', None, None
        if 'question' in flask.request.json:
            question = flask.request.json['question']

            qa_pair = QApair(question, '', '', 'id', self.parser)
            outputs, done, num_pipelines = FreeQuestionSurvey.pipeline.run(qa_pair)
            self.pipeline_data[userid] = (outputs, done, num_pipelines)
            if num_pipelines > 0:
                while len(outputs.queue) == 0 and len(done.queue) < num_pipelines:
                    time.sleep(1)

            pipeline_output = [item for output in outputs.queue for item in output[2]]
            self.interaction_data[userid] = InteractionManager(pipeline_output, kb=self.kb,
                                                               sparql_parser=self.parser.parse_sparql,
                                                               interaction_type=self.interaction_types,
                                                               strategy=self.strategy)

            io, query = self.interaction_data[userid].get_interaction_option()

        output = self.handle_IO(question, None, query, io)
        output['task'] = flask.request.json['task']
        # output['stats'] = {'total': 1, 'answered': 0}
        return flask.jsonify(output)

    @route('interact', methods=['POST'])
    def interact(self):
        if not flask.request.json:
            flask.abort(400)
        userid = flask.request.json['userid']
        if flask.request.json['answer'] == 'uncertain':
            answer = None
        else:
            answer = flask.request.json['answer'] == 'True'

        current_io = None
        if len(self.pipeline_data[userid][0].queue) > len(self.interaction_data[userid].pipeline_results):
            current_io = self.interaction_data[userid].last_option
            pipeline_output = [item for output in self.pipeline_data[userid][0].queue for item in output[2]]
            self.interaction_data[userid] = InteractionManager(pipeline_output, kb=self.kb,
                                                               sparql_parser=self.parser.parse_sparql,
                                                               interaction_type=self.interaction_types,
                                                               strategy=self.strategy)
            # TODO: apply previously done interactions
            for io, io_answer in self.interaction_history:
                self.interaction_data[userid].interact(io_answer, io)

        else:
            self.interaction_history.append((self.interaction_data[userid].last_option, answer))

        if self.interaction_data[userid].interact(answer, current_io):
            io, query = self.interaction_data[userid].get_interaction_option()
            question = self.interaction_data[userid].pipeline_results[-1]['question']

            return flask.jsonify(self.handle_IO(question, None, query, io))
        else:
            return flask.jsonify({'command': 'next_question'})

    def handle_IO(self, question, qid, query, io):
        result = {'question': question, 'query': query, 'qid': qid}
        if io is None:
            # there is no IO, but there is one valid query
            if query is not None:
                result['IO'] = {'surface': query, 'values': []}
        elif io.type == 'linked' or io.type == 'linked_type':
            start, length = map(int, [item.strip('[]') for item in io.value.surface_form.split(',')])
            surface = question[start:start + length]
            if io.type == 'linked_type':
                surface = 'type of "{}"'.format(surface)
            result['IO'] = {'surface': surface,
                            'values': [io.value.uris[0].uri]}
        elif io.type == 'type':
            result['IO'] = {'surface': 'question_type', 'values': [io.value]}
        elif io.type == 'query':
            result['IO'] = {'surface': io.value.query, 'values': []}

        if query is not None:
            if FreeQuestionSurvey.pipeline is not None:
                query_results = FreeQuestionSurvey.pipeline.kb.query(query + ' LIMIT 10')
                head_var = query_results[1]['head']['vars'][0]
                result['answer'] = [item[head_var]['value'].replace('http://dbpedia.org/resource/', '') for item in
                                    query_results[1]['results']['bindings']]
        return result
