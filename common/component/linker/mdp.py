from common.utility.utils import Utils
from common.component.chunker.chunker import Chunker
import config
import ujson as json
import os


class MDP(Chunker):
    def __init__(self, endpoint=config.config["MDP"]["endpoint"], cache_path="", use_cache=True,
                 connecting_relations=False):
        self.endpoint = endpoint
        self.connecting_relations = connecting_relations
        self.cache_path = cache_path
        self.use_cache = use_cache
        self.cache = {}
        if self.use_cache:
            Utils.makedirs(cache_path)
            self.cache_path = os.path.join(cache_path, "mdp-{}.cache".format(connecting_relations))
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
        input = {'question': question, 'k': 10, 'connecting_relations': self.connecting_relations}

        output = {'entities': [], 'relations': [], 'chunks': []}
        if id not in self.cache or not self.use_cache:
            result = Utils.call_web_api(self.endpoint, input)
            if result is None:
                return output
            self.cache[id] = result
            self.__save_cache()
        if self.cache[id] is None:
            return output
        else:
            return self.cache[id]

    def get_phrases(self, question):
        return self.__hit_endpoint(question, None)["chunks"]

    def link_entities(self, question, chunks=None):
        return self.__hit_endpoint(question, chunks)["entities"]

    def link_relations(self, question, chunks=None):
        return self.__hit_endpoint(question, chunks)["relations"]

    def link_entities_relations(self, question, chunks=None):
        return {"relations": self.link_relations(question, chunks),
                "entities": self.link_entities(question, chunks)}


if __name__ == '__main__':
    print('MDP')
    mdp = MDP('http://localhost:5006/link', '', False)
    print(mdp.link_entities_relations('Who is the father of Barak Obama?'))
