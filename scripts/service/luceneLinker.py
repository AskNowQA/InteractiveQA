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
from common.utility.luceneSearch import LuceneSearch
import pickle as pk

app = flask.Flask(__name__)
linker = None


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


@app.route('/iqa/api/v1.0/link', methods=['POST'])
def link():
    if not flask.request.json:
        flask.abort(400)

    result = linker[flask.request.json['index']].search(flask.request.json['chunk'],
                           use_ngram=flask.request.json['use_ngram'],
                           use_stemmer=flask.request.json['use_stemmer'])

    return json.dumps(list(result))


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    parser = argparse.ArgumentParser(description='Link input question into entities/relations')
    parser.add_argument("--port", help="port", default=5005, type=int, dest="port")
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--index", help="index path ",
                        default="output/idx_ent_ngram/;output/idx_rel_ngram/;output/idx_rel_stemmer/", dest="index")

    args = parser.parse_args()
    logger.info(args)
    linker = {}
    for index_path in args.index.split(';'):
        index = index_path[index_path.index('/') + 1:-1]
        linker[index] = LuceneSearch(index_path=os.path.join(args.base_path, index_path),
                                     input_file_path='',
                                     create_index=False,
                                     use_ngram=False,
                                     use_stemmer=False)
    # print(list(linker['idx_ent_ngram'].search('barak obama', use_ngram=True)))
    # print(list(linker['idx_rel_ngram'].search('president', use_ngram=True)))
    # print(list(linker['idx_rel_stemmer'].search('president', use_stemmer=True)))
    app.run(debug=False, port=args.port)
