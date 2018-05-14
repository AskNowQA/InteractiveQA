from common.utility.utils import Utils
import config
import json
import os


class EARL:
    def __init__(self, endpoint=config.config["EARL"]["endpoint"], cache_path="", use_cache=True):
        self.endpoint = endpoint
        self.cache_path = cache_path
        self.use_cache = use_cache
        self.cache = {}
        if self.use_cache:
            Utils.makedirs(cache_path)
            self.cache_path = os.path.join(cache_path, "earl.cache")
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
        input = {'nlquery': question}
        if chunks is not None and isinstance(chunks, list) and len(chunks) > 0:
            input['chunks'] = chunks
            id += "".join(chunks)

        if id not in self.cache or not self.use_cache:
            self.cache[id] = Utils.call_web_api(self.endpoint, input)
            self.__save_cache()
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
