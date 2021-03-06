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
            input['erpredictions'] = chunks
            id += "".join([item['chunk'] for item in chunks])
            # for chunk in chunks:
            #     if chunk.lower() in question.lower():
            #         chunk_idx = question.lower().index(chunk.lower())
            #         question = question.replace(question[chunk_idx:chunk_idx + len(chunk)], chunk)
            input['nlquery'] = question

        if id not in self.cache or not self.use_cache:
            result = Utils.call_web_api(self.endpoint, input)
            output = {'entities': [], 'relations': []}
            if result is None:
                return output
            last_idx = 0
            question_lower = question.lower()
            for idx, chunk in enumerate(chunks):
                chunk_text = chunk['chunk'].lower()
                if chunk_text in question_lower:
                    chunk_idx = question_lower.index(chunk_text, last_idx)
                else:
                    chunk_idx = 0
                surface_info = [chunk_idx, len(chunk_text)]
                uris = [{'confidence': item[0], 'uri': item[1]} for item in result['rerankedlists'][str(idx)]]
                tmp = {'surface': surface_info, 'uris': uris}
                if result['ertypes'][idx] == 'entity':
                    output['entities'].append(tmp)
                else:
                    output['relations'].append(tmp)

            self.cache[id] = output
            self.__save_cache()
        if self.cache[id] is None:
            return {'entities': [], 'relations': []}
        else:
            return self.cache[id]

    def chunk(self, question):
        return []

    def link_entities(self, question, chunks=None):
        # if chunks is not None:
        #     chunks = [item['chunk'] if item['class'] == 'relation' else item['chunk'].title() for item in chunks]
        return self.__hit_endpoint(question, chunks)["entities"]

    def link_relations(self, question, chunks=None):
        # if chunks is not None:
        #     chunks = [item['chunk'] if item['class'] == 'relation' else item['chunk'].title() for item in chunks]
        return self.__hit_endpoint(question, chunks)["relations"]

    def link_entities_relations(self, question, chunks=None):
        if chunks is None:
            chunks = self.chunk(question)
        return {"relations": self.link_relations(question, chunks),
                "entities": self.link_entities(question, chunks)}
