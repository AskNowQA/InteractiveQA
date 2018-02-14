from __future__ import division
from __future__ import print_function
import os
import logging.config


class Struct(object): pass


class Utils:
    @staticmethod
    def makedirs(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return None

    @staticmethod
    def setup_logging(
            default_path='logging.json',
            default_level=logging.INFO,
            env_key='LOG_CFG'
    ):
        """Setup logging configuration

        """
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
