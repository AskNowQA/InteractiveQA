import itertools
from common.utility.utils import Utils


class LuceneLinker:
    __special_chars = ['\n', '\r', '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '_', '.', '/', ':', ';',
                       '=', '?', '@', '~'] + list(map(str, range(0, 10)))

    def __init__(self, index, use_ngram=False, use_stemmer=False):
        self.index = index
        self.use_ngram = use_ngram
        self.use_stemmer = use_stemmer

    def search(self, term):
        output = Utils.call_web_api('http://127.0.0.1:5005/iqa/api/v1.0/link',
                                    {'index': self.index,
                                     'chunk': term,
                                     'use_ngram': self.use_ngram,
                                     'use_stemmer': self.use_stemmer})
        return output

    def __link(self, question, item_type, chunks=None):
        results = []
        for chunk in chunks:
            if chunk['class'] == item_type:
                candidate_items = itertools.islice(self.search(chunk['chunk']), 20)
                candidate_items = [{'confidence': item[1], 'uri': item[0]} for item in candidate_items]
                idx = 0
                if chunk['chunk'] in question:
                    idx = question.index(chunk['chunk'])
                if len(candidate_items) > 0:
                    results.append({'surface': [idx, len(chunk['chunk'])], 'uris': candidate_items})
        return results

    def link_entities(self, question, chunks=None):
        return self.__link(question, 'entity', chunks)

    def link_relations(self, question, chunks=None):
        return self.__link(question, 'relation', chunks)

    def link_entities_relations(self, question, chunks=None):
        return {"relations": self.link_relations(question, chunks),
                "entities": self.link_entities(question, chunks)}
