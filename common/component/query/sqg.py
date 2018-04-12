from common.utility.utils import Utils
import json
import os


class SQG:
    def __init__(self, endpoint='http://localhost:5001/qg/api/v1.0/query', cache_path="", use_cache=True):
        self.endpoint = endpoint
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
        input = {'question': question, "entities": entities, "relations": relations}

        if id not in self.cache or not self.use_cache:
            self.cache[id] = Utils.call_web_api(self.endpoint, input)
            self.__save_cache()
        return self.cache[id]
