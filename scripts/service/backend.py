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

global pipeline_path
global kb
global dataset
global interaction_types
global strategy

app = flask.Flask(__name__)
app.secret_key = 'sec key'
interaction_data = dict()


def handle_IO(question, query, io):
    result = {'question': question, 'query': query}
    if io is None:
        pass
    elif io.type == 'linked':
        start, length = map(int, [item.strip('[]') for item in io.value.surface_form.split(',')])

        result['IO'] = {'surface': question[start:start + length],
                        'values': [io.value.uris[0].uri]}
    elif io.type == 'type':
        result['IO'] = {'surface': 'Type of Question', 'values': [io.value]}
    return result


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


@app.route('/iqa/ui/v1.0/start', methods=['POST'])
def start():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']

    question_id = 'f0a9f1ca14764095ae089b152e0e7f12'
    with open(os.path.join(pipeline_path, ('{0}.pickle'.format(question_id))), 'r') as file_handler:
        interaction_data[userid] = InteractionManager(pk.load(file_handler), kb, dataset.parser.parse_sparql,
                                                      interaction_types, strategy)

    question = interaction_data[userid].pipeline_results[-1][0]
    io, query = interaction_data[userid].get_interaction_option()

    return json.dumps(handle_IO(question, query, io))


@app.route('/iqa/ui/v1.0/interact', methods=['POST'])
def interact():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']
    interaction_data[userid].interact(flask.request.json['answer'] == 'True')
    io, query = interaction_data[userid].get_interaction_option()
    question = interaction_data[userid].pipeline_results[-1][0]

    return json.dumps(handle_IO(question, query, io))


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
    dataset = LC_Qaud_Linked(auto_load=False)
    interaction_types = [[False, True], [True, True]]
    strategy = 'InformationGain'

    app.run(debug=False, port=args.port)
