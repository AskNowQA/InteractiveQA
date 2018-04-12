import json
import re
from common.container.qapair import QApair
from common.container.uri import Uri
from common.kb.dbpedia import DBpedia


class LC_Qaud_Linked:
    def __init__(self, path="./data/LC-QuAD/linked.json"):
        self.raw_data = []
        self.qapairs = []
        self.path = path
        self.parser = LC_Qaud_LinkedParser()
        self.load()
        self.parse()

    def load(self):
        with open(self.path) as data_file:
            self.raw_data = json.load(data_file)

    def parse(self):
        for raw_row in self.raw_data:
            self.qapairs.append(
                QApair(raw_row["question"], raw_row["sparql_query"], raw_row, raw_row["id"],
                       self.parser))

    def print_pairs(self, n=-1):
        for item in self.qapairs[0:n]:
            print item
            print ""


class LC_Qaud_LinkedParser():
    def __init__(self):
        self.kb = DBpedia()

    def parse_question(self, raw_question):
        return raw_question

    def parse_sparql(self, raw_query):
        uris = [Uri(raw_uri, self.kb.parse_uri) for raw_uri in re.findall('(<[^>]*>|\?[^ ]*)', raw_query)]
        return raw_query, True, uris
