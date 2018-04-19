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

app = flask.Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


@app.route('/iqa/ui/v1.0/start', methods=['POST'])
def start():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']

    result = {'question': 'Name the municipality of Robert Clemente Bridge?',
              'IO': {'surface': 'Robert Clemente Bridge',
                     'values': ['Robert Clemente Bridge', 'Robert Clemente Community School']}}

    return json.dumps(result)


@app.route('/iqa/ui/v1.0/interact', methods=['POST'])
def interact():
    if not flask.request.json:
        flask.abort(400)

    userid = flask.request.json['userid']
    io = flask.request.json['IO']
    result = {'IO': {'surface': 'municipality',
                     'values': ['municipality', 'city']}}

    return json.dumps(result)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    app.run(debug=False, port=args.port)
