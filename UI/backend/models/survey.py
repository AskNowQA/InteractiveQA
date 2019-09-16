import os
import pickle as pk

import flask
from flask_classful import FlaskView, route

from common.interaction.interactionManager import InteractionManager


class Survey(FlaskView):
    route_base = 'survey'
    interaction_data = dict()
    dataset = None
    kb = None
    strategy = None
    pipeline_path = None
    book_keeper = None

    @route('start', methods=['POST'])
    def start(self):

        if not flask.request.json:
            flask.abort(400)

        userid = flask.request.json['userid']
        qid = None
        if 'qid' in flask.request.json:
            qid = flask.request.json['qid']
        strategy = Survey.strategy
        if 'strategy' in flask.request.json:
            if flask.request.json['strategy'] in ['InformationGain', 'OptionGain', 'Probability']:
                strategy = flask.request.json['strategy']

        question_id, total, answered = self.book_keeper.new_question(userid, qid)
        if question_id is None:
            return flask.jsonify({'command': 'end_survey'})

        with open(os.path.join(self.pipeline_path, ('{0}.pickle'.format(question_id))), 'rb') as file_handler:
            interaction_types = [[False, True], [True, True]]
            self.interaction_data[userid] = InteractionManager(pk.load(file_handler), kb=self.kb,
                                                               sparql_parser=self.dataset.parser.parse_sparql,
                                                               interaction_type=interaction_types, strategy=strategy,
                                                               target_query=self.dataset.get_by_id(question_id)[0])

        question = self.interaction_data[userid].pipeline_results[0][-1][0]
        io, query = self.interaction_data[userid].get_interaction_option()

        output = self.handle_IO(question, question_id, query, io)
        output['stats'] = {'total': total, 'answered': answered}
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
        if self.interaction_data[userid].interact(answer):
            io, query = self.interaction_data[userid].get_interaction_option()
            if io is None and query is None:
                return flask.jsonify({'command': 'next_question'})
            question = self.interaction_data[userid].pipeline_results[0][-1][0]

            return flask.jsonify(self.handle_IO(question, None, query, io))
        else:
            return flask.jsonify({'command': 'next_question'})

    @route('correct', methods=['POST'])
    def correct(self):
        if not flask.request.json:
            flask.abort(400)

        userid = flask.request.json['userid']
        # TODO: Mark current query as selected query by the user
        return flask.make_response(flask.jsonify({}), 200)

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
        return result
