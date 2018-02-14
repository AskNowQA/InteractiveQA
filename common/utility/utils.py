from __future__ import division
from __future__ import print_function
import os
import logging.config
import json
import urllib2


class Struct(object): pass


class Utils:
    @staticmethod
    def makedirs(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return None

    @staticmethod
    def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
        path = default_path
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)

    @staticmethod
    def call_web_api(endpoint, input):
        req = urllib2.Request(endpoint)
        req.add_header('Content-Type', 'application/json')
        # try:
        response = urllib2.urlopen(req, json.dumps(input))
        response = response.read()
        response = json.loads(response)
        return response
        # except:
        #     return None
