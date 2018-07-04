import sys
import os

module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import flask
import argparse
import logging
import pickle as pk
import json
from common.utility.utils import Utils
from common.kb.dbpedia import DBpedia
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.interaction.interactionManager import InteractionManager
from common.interaction.bookKeeper import BookKeeper

global pipeline_path
global kb
global dataset
global interaction_types
global strategy
global book_keeper

app = flask.Flask(__name__)
app.secret_key = 'sec key'
interaction_data = dict()


def handle_IO(question, qid, query, io):
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


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


@app.route('/iqa/ui/v1.0/start', methods=['POST'])
def start():
    global strategy, book_keeper
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']
    qid = None
    if 'qid' in flask.request.json:
        qid = flask.request.json['qid']
    if 'strategy' in flask.request.json:
        if flask.request.json['strategy'] in ['InformationGain', 'OptionGain', 'Probability']:
            strategy = flask.request.json['strategy']

    question_id, total, answered = book_keeper.new_question(userid, qid)
    if question_id is None:
        return json.dumps({'command': 'end_survey'})
    with open(os.path.join(pipeline_path, ('{0}.pickle'.format(question_id))), 'r') as file_handler:
        interaction_data[userid] = InteractionManager(pk.load(file_handler), kb=kb,
                                                      sparql_parser=dataset.parser.parse_sparql,
                                                      interaction_type=interaction_types, strategy=strategy,
                                                      target_query=[qapair for qapair in dataset.qapairs if
                                                                    qapair.id == question_id][0])

    question = interaction_data[userid].pipeline_results[-1][0]
    io, query = interaction_data[userid].get_interaction_option()

    output = handle_IO(question, question_id, query, io)
    output['stats'] = {'total': total, 'answered': answered}
    return json.dumps(output)


@app.route('/iqa/ui/v1.0/interact', methods=['POST'])
def interact():
    if not flask.request.json:
        flask.abort(400)
    userid = flask.request.json['userid']

    if flask.request.json['answer'] == 'uncertain':
        answer = None
    else:
        answer = flask.request.json['answer'] == 'True'
    if interaction_data[userid].interact(answer):
        io, query = interaction_data[userid].get_interaction_option()
        question = interaction_data[userid].pipeline_results[-1][0]

        return json.dumps(handle_IO(question, None, query, io))
    else:
        return json.dumps({'command': 'next_question'})


@app.route('/iqa/ui/v1.0/correct', methods=['POST'])
def correct():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']
    # TODO: Mark current query as selected query by the user
    return flask.make_response(flask.jsonify({}), 200)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--port", help="port", default=5002, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    pipeline_path = os.path.join(args.base_path, 'output', 'pipeline')
    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    dataset = LC_Qaud_Linked(os.path.join(args.base_path, 'data', 'LC-QuAD', 'linked.json'))
    interaction_types = [[False, True], [True, True]]
    strategy = 'InformationGain'
    book_keeper = BookKeeper(os.path.join(args.base_path, 'UI', 'database', 'IQA.db'))

    app.run(debug=False, port=args.port)
