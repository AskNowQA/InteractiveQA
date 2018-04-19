from common.utility.utils import Utils
import config
import json
import os


class SQG:
    def __init__(self, endpoint=config.config["SQG"]['endpoint'], timeout=config.config["SQG"]['timeout'],
                 cache_path="", use_cache=True):
        self.endpoint = endpoint
        self.timeout = timeout
        self.cache_path = cache_path
        self.use_cache = use_cache
        self.cache = {}
        if self.use_cache:
            Utils.makedirs(cache_path)
            self.cache_path = os.path.join(cache_path, "sqg.cache")
            self.__load_cache()

    def __load_cache(self):
        try:
            with open(self.cache_path) as cache_file:
                self.cache = json.load(cache_file)
        except:
            self.cache = {}

    def __save_cache(self):
        try:
            with open(self.cache_path, "w") as cache_file:
                json.dump(self.cache, cache_file)
            return True
        except:
            return False

    def build_query(self, question, entities=[], relations=[]):
        id = question
        input = {'question': question, "entities": entities, "relations": relations, 'timeout': self.timeout,
                 'use_cache': config.config["SQG"]['use_sqg_cache']}

        if id not in self.cache or not self.use_cache:
            result = Utils.call_web_api(self.endpoint, input)
            self.cache[id] = {'queries': []} if result is None else result
            self.__save_cache()
        return self.cache[id]
