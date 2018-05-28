import re
import os
import json
from itertools import takewhile
from tqdm import tqdm
from common.parser.lc_quad_linked import LC_Qaud_Linked


class RNLIWOD:
    def __init__(self, log_path='./data/LC-QuAD/relnliodLogs', dataset_path='./data/LC-QuAD/linked_3200.json'):
        self.annotation_file = os.path.join(log_path, 'RNLIWORD.json')
        if not os.path.exists(self.annotation_file):
            self.__create_annotation_file(log_path, dataset_path)

        with open(self.annotation_file, "r") as annotations_file:
            raw_data = json.load(annotations_file)
            self.annotations = {item['question']: item['relations'] for item in raw_data}

    @staticmethod
    def __get_entries(name, path):
        with open(path) as file:
            for line in file:
                if "http://www.wdaqua.eu/qa#" + name in line:
                    buf = [line]
                    buf.extend(takewhile(str.strip, file))  # read until blank line
                    yield re.findall(r'<(http://dbpedia[^>]+)>', ''.join(buf))

    def __create_annotation_file(self, log_path, dataset_path):
        ds = LC_Qaud_Linked(path=dataset_path)

        input_files = os.listdir(log_path)
        input_files.sort()

        annotations = []
        i = 0
        for name in tqdm(input_files):
            # print i
            relations = list(RNLIWOD.__get_entries("AnnotationOfRelation", os.path.join(log_path, name)))
            if len(relations) > 0:
                relations = [{"surface": [0, 0], "uris": [{"uri": item[0], "confidence": 1}]} for item in
                             relations if len(item) > 0]
                annotations.append(
                    {"question": ds.qapairs[i].question.text, "relations": relations})
            i += 1
        with open(self.annotation_file, "w") as output_file:
            json.dump(annotations, output_file)

    def link_relations(self, question, chunks=None):
        return self.annotations[question] if question in self.annotations else []
