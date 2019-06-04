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

from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.utility.utils import Utils
from common.component.chunker.classifierChunkParser import ClassifierChunkParser


# from common.component.chunker.SENNAChunker import SENNAChunker


class LuceneSearch:
    __special_chars = ['\n', '\r', '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '_', '.', '/', ':', ';',
                       '=', '?', '@', '~'] + list(map(str, range(0, 10)))

    def __init__(self, index_path, input_file_path=None, create_index=False, use_ngram=False, use_stemmer=False):
        # assert lucene.getVMEnv() or lucene.initVM()
        lucene.initVM()
        self.env = lucene.getVMEnv()

        self.index_path = index_path
        self.stemmer = nltk.stem.porter.PorterStemmer()

        self.transorm_func = None
        if use_ngram:
            if use_stemmer:
                self.transorm_func = lambda x: self.n_grams(u" ".join(self.split_and_stem(x)))
            else:
                self.transorm_func = self.n_grams
        elif use_stemmer:
            self.transorm_func = self.split_and_stem

        if create_index:
            self.create_index(input_file_path)

        directory = store.FSDirectory.open(File(index_path).toPath())
        analyzer = analysis.standard.StandardAnalyzer()
        print(directory)
        self.indexer = engine.Indexer(directory=directory, analyzer=analyzer)

        self.q = 0

    def search(self, term, index=None, use_ngram=None, use_stemmer=None):
        self.env.attachCurrentThread()
        transorm_func = None
        if use_ngram:
            if use_stemmer:
                transorm_func = lambda x: self.n_grams(u" ".join(self.split_and_stem(x)))
            else:
                transorm_func = self.n_grams
        elif use_stemmer:
            transorm_func = self.split_and_stem

        try:
            term = term.replace('\r\n', '').replace('?', '')
            if len(term) <= 2:
                return
            if transorm_func is not None:
                term = transorm_func(term)
                query = ' '.join(term)
            else:
                query = term
            hits = self.indexer.search(query, field='ngram', count=100, maxscore=True)
            for hit in hits:  # hits support mapping interface
                yield hit['uri'].replace('\n', ''), hit.score / hits.maxscore
        except Exception as err:
            print(err)
            self.q += 1
            return []

    def create_index(self, input_file_path):
        directory = store.FSDirectory.open(File(self.index_path).toPath())
        analyzer = analysis.standard.StandardAnalyzer()
        indexer = engine.Indexer(directory=directory, analyzer=analyzer)
        indexer.set('term', engine.Field.Text, stored=True)
        indexer.set('uri', engine.Field.Text, stored=True)
        indexer.set('ngram', engine.Field.Text, stored=True)

        with io.open(input_file_path, 'r', encoding='utf-8') as input_file:
            for line in tqdm(input_file):
                uri = line.replace('\n', '')
                name = uri[line.rindex('/') + 1:]
                ngram = name
                if self.transorm_func is not None:
                    ngram = self.transorm_func(name)
                indexer.add(term=name, uri=uri, ngram=ngram)
            indexer.commit()

    def n_grams(self, term, n=3):
        term = term.lower()
        for i in range(len(term) - n + 1):
            yield term[i:i + n]

    def split_and_stem(self, text):
        for char in LuceneSearch.__special_chars:
            text = text.replace(char, ' ')
        results = []
        buffer = ''
        for char in text:
            if char.isupper() or char == ' ':
                results.append(buffer.strip())
                buffer = ''
            buffer += char

        results.append(buffer)
        results = [item.strip().lower() for item in results if len(item.strip()) > 0]
        try:
            return [self.stemmer.stem(item) for item in results]
        except:
            pass
        return results


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    parser = argparse.ArgumentParser(description='Generate linker output')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument('--path', help='input dataset', default='data/LC-QuAD/linked2843.json', dest='ds_path')
    parser.add_argument('--output', help='output path',
                        default='data/LC-QuAD/lucence_ent_stemmer_classifier.json',
                        dest='output_path')
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked_IOB.pk",
                        dest="gold_chunk")
    parser.add_argument("--type", help="entity|relation", default="entity", dest="link_type")
    parser.add_argument("--index", help="index path ", default="output/index_ngram/", dest="index")
    parser.add_argument("--input", help="input file path to create the index ",
                        default="data/dbpedia/labels_en_entities.ttl", dest="input")
    parser.add_argument('--create_idx', dest='create_idx', default=False, action='store_true')
    parser.add_argument('--ngram', dest='ngram', default=False, action='store_true')
    parser.add_argument('--stemmer', dest='stemmer', default=False, action='store_true')
    args = parser.parse_args()

    linker = LuceneSearch(index_path=os.path.join(args.base_path, args.index),
                          input_file_path=os.path.join(args.base_path, args.input),
                          create_index=args.create_idx,
                          use_ngram=args.ngram,
                          use_stemmer=args.stemmer)

    for item in linker.search('Germany'):
        print(item)

    # ds = LC_Qaud_Linked(os.path.join(args.base_path, args.ds_path))

    # with open(os.path.join(args.base_path, args.gold_chunk)) as data_file:
    #     gold_chunk_dataset = pk.load(data_file)
    # chunker = GoldChunker({item[0]: item[1:] for item in gold_chunk_dataset})

    # chunker = ClassifierChunkParser([], os.path.join(args.base_path, args.model))
    # chunker = SENNAChunker()

    # results = []
    # for qapair in tqdm(ds.qapairs):
    #     chunks = chunker.get_phrases(qapair.question.raw_question)
    #     result = {'entities': [], 'relations': [], 'question': qapair.question.raw_question}
    #     relations = []
    #     for chunk in chunks:
    #         if chunk['class'] == args.link_type:
    #             uris = []
    #             idx = 0
    #             for item in linker.search(chunk['chunk']):
    #                 uris.append({'confidence': item[1], 'uri': item[0]})
    #                 idx += 1
    #                 if idx > 10:
    #                     break
    #             relations.append({'surface': [0, 0], 'uris': uris})
    #     if args.link_type == 'entity':
    #         result['entities'] = relations
    #     elif args.link_type == 'relation':
    #         result['relations'] = relations
    #     results.append(result)
    # print(linker.q)
    # with open(os.path.join(args.base_path, args.output_path), 'w') as data_file:
    #     json.dump(results, data_file)
