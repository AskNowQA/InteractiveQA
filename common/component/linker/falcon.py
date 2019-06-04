from common.utility.utils import Utils
import config
import json
import os


class Falcon:
    def __init__(self, endpoint=config.config["Falcon"]["endpoint"], cache_path="", use_cache=True):
        self.endpoint = endpoint
        self.cache_path = cache_path
        self.use_cache = use_cache
        self.cache = {}
        if self.use_cache:
            Utils.makedirs(cache_path)
            self.cache_path = os.path.join(cache_path, "falcon.cache")
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

    def __hit_endpoint(self, question, chunks):
        id = question
        input = {'text': question}

        if id not in self.cache or not self.use_cache:
            result = Utils.call_web_api(self.endpoint, input)
            output = {'entities': [], 'relations': []}
            question_lower = question.lower()
            if result is None:
                return output
            output = {'entities': [{'surface': [question_lower.index(item[1].lower()), len(item[1])] if
            item[1].lower() in question_lower else [0, 0],
                                    'uris': [{'confidence': 1.0, 'uri': item[0]}]} for item in result['entities']],
                      'relations': [{'surface': [question_lower.index(item[1].lower()), len(item[1])] if
                      item[1].lower() in question_lower else [0, 0],
                                     'uris': [{'confidence': 1.0, 'uri': item[0]}]} for item in result['relations']]}
            self.cache[id] = output
            self.__save_cache()
        if self.cache[id] is None:
            return {'entities': [], 'relations': []}
        else:
            return self.cache[id]

    def chunk(self, question):
        return []

    def link_entities(self, question, chunks=None):
        if chunks is not None:
            chunks = [item['chunk'] for item in chunks]
        return self.__hit_endpoint(question, chunks)["entities"]

    def link_relations(self, question, chunks=None):
        if chunks is not None:
            chunks = [item['chunk'] for item in chunks]
        return self.__hit_endpoint(question, chunks)["relations"]

    def link_entities_relations(self, question, chunks=None):
        if chunks is None:
            chunks = self.chunk(question)
        return {"relations": self.link_relations(question, chunks),
                "entities": self.link_entities(question, chunks)}
