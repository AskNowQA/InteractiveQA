import lucene
from lupyne import engine
from lupyne.engine import Query
from java.io import File
from org.apache.lucene import analysis, index, queryparser, search, store
from tqdm import tqdm
import nltk
import argparse
import logging
import pickle as pk
import os
import json
import itertools
import io
from common.component.chunker.goldChunker import GoldChunker
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.utility.utils import Utils
from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.SENNAChunker import SENNAChunker
from common.utility.luceneSearch import LuceneSearch


class LuceneLinker:
    __special_chars = ['\n', '\r', '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '_', '.', '/', ':', ';',
                       '=', '?', '@', '~'] + map(str, range(0, 10))

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

# if __name__ == '__main__':
#     logger = logging.getLogger(__name__)
#     Utils.setup_logging()
#
#     parser = argparse.ArgumentParser(description='Generate linker output')
#     parser.add_argument("--base_path", help="base path", default="../../../", dest="base_path")
#     parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
#                         dest="model")
#     parser.add_argument('--path', help='input dataset', default='data/LC-QuAD/linked2843.json', dest='ds_path')
#     parser.add_argument('--output', help='output path',
#                         default='data/LC-QuAD/lucence_ent_stemmer_classifier.json',
#                         dest='output_path')
#     parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked_IOB.pk",
#                         dest="gold_chunk")
#     parser.add_argument("--type", help="entity|relation", default="entity", dest="link_type")
#     parser.add_argument("--index", help="index path ", default="output/index_ngram/", dest="index")
#     parser.add_argument("--input", help="input file path to create the index ",
#                         default="data/dbpedia/labels_en_entities.ttl", dest="input")
#     parser.add_argument('--create_idx', dest='create_idx', default=False, action='store_true')
#     parser.add_argument('--ngram', dest='ngram', default=False, action='store_true')
#     parser.add_argument('--stemmer', dest='stemmer', default=False, action='store_true')
#     args = parser.parse_args()
#
#     linker = LuceneLinker(index_path=os.path.join(args.base_path, args.index),
#                           input_file_path=os.path.join(args.base_path, args.input),
#                           create_index=args.create_idx,
#                           use_ngram=args.ngram,
#                           use_stemmer=args.stemmer)
#
#     # for item in linker.search('succeed'):
#     #     print item
#
#     ds = LC_Qaud_Linked(os.path.join(args.base_path, args.ds_path))
#
#     with open(os.path.join(args.base_path, args.gold_chunk)) as data_file:
#         gold_chunk_dataset = pk.load(data_file)
#     # chunker = GoldChunker({item[0]: item[1:] for item in gold_chunk_dataset})
#
#     chunker = ClassifierChunkParser([], os.path.join(args.base_path, args.model))
#     # chunker = SENNAChunker()
#
#     results = []
#     for qapair in tqdm(ds.qapairs):
#         chunks = chunker.get_phrases(qapair.question.raw_question)
#         result = {'entities': [], 'relations': [], 'question': qapair.question.raw_question}
#         relations = []
#         for chunk in chunks:
#             if chunk['class'] == args.link_type:
#                 uris = []
#                 idx = 0
#                 for item in linker.search(chunk['chunk']):
#                     uris.append({'confidence': item[1], 'uri': item[0]})
#                     idx += 1
#                     if idx > 10:
#                         break
#                 relations.append({'surface': [0, 0], 'uris': uris})
#         if args.link_type == 'entity':
#             result['entities'] = relations
#         elif args.link_type == 'relation':
#             result['relations'] = relations
#         results.append(result)
#     print linker.q
#     with open(os.path.join(args.base_path, args.output_path), 'w') as data_file:
#         json.dump(results, data_file)
