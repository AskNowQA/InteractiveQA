#!flask/bin/python
import sys
import os

module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import flask
import argparse
import logging
import json
from common.utility.utils import Utils
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.goldChunker import GoldChunker
import pickle as pk

app = flask.Flask(__name__)
chunkers = None


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


@app.route('/iqa/api/v1.0/chunk', methods=['POST'])
def chunk():
    if not flask.request.json:
        flask.abort(400)

    question = flask.request.json['nlquery']
    result = []
    for chunker in chunkers:
        result.append({"name": type(chunker).__name__, "result": chunker.get_phrases(question)})

    print question
    print result
    print

    return json.dumps(result)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    base_dir = "../../"
    model_dir = os.path.join(base_dir, "models")
    Utils.makedirs(model_dir)

    parser = argparse.ArgumentParser(description='Chunk input question into phrases')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    tagger_filename = os.path.join(model_dir, "ClassifierChunkParser.tagger.model")
    # Only for LC-QuAD
    with open('../../data/LC-QUAD/linked2843_IOB.pk') as data_file:
        dataset = pk.load(data_file)

    chunkers = [SENNAChunker(), ClassifierChunkParser([], tagger_filename),
                GoldChunker({item[0]: item[1:] for item in dataset})]

    app.run(debug=False, port=args.port)
