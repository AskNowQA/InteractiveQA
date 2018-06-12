import json
import re
import os
from common.container.qapair import QApair
from common.container.uri import Uri
from common.kb.dbpedia import DBpedia


class LC_Qaud_Linked:
    def __init__(self, path='./data/LC-QuAD/linked.json', auto_load=True):
        self.raw_data = []
        self.qapairs = []
        self.path = path
        self.parser = LC_Qaud_LinkedParser()
        if auto_load:
            self.load()
            self.parse()

    def load(self):
        with open(self.path) as data_file:
            self.raw_data = json.load(data_file)

    def parse(self):
        for raw_row in self.raw_data:
            question = raw_row['question'] if 'question' in raw_row else raw_row['corrected_question']
            query = raw_row['sparql_query'].replace('https://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                                                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
            id = raw_row['id'] if 'id' in raw_row else raw_row['_id']
            self.qapairs.append(QApair(question, query, raw_row, id, self.parser))

    def print_pairs(self, n=-1):
        for item in self.qapairs[0:n]:
            print item
            print ''


class LC_Qaud_LinkedParser():
    def __init__(self):
        self.kb = DBpedia()

    def parse_question(self, raw_question):
        return raw_question

    def parse_sparql(self, raw_query):
        uris = [Uri(raw_uri, self.kb.parse_uri) for raw_uri in re.findall('(<[^>]*>|\?[^ ]*)', raw_query)]
        return raw_query, True, uris
