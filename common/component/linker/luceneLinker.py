import lucene
from lupyne import engine
from lupyne.engine import Query
from java.io import File
from org.apache.lucene import analysis, index, queryparser, search, store
from tqdm import tqdm

from common.component.chunker.goldChunker import GoldChunker
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.utility.utils import Utils
import argparse
import logging
import pickle as pk
import os
import json
import itertools
from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.SENNAChunker import SENNAChunker


class LuceneLinker:
    def __init__(self, index_path, input_file_path=None, create_index=False):
        assert lucene.getVMEnv() or lucene.initVM()
        self.index_path = index_path

        if create_index:
            self.create_index(input_file_path)

        directory = store.FSDirectory.open(File(index_path).toPath())
        analyzer = analysis.standard.StandardAnalyzer()
        self.indexer = engine.Indexer(directory=directory, analyzer=analyzer)
        self.q = 0

    def link_entities(self, question, chunks=None):
        return []

    def link_relations(self, question, chunks=None):
        results = []
        for chunk in chunks:
            if chunk['class'] == 'relation':
                candidate_items = itertools.islice(self.search(chunk['chunk']), 10)
                candidate_items = [{'confidence': 0.5, 'uri': item} for item in candidate_items]
                idx = 0
                if chunk['chunk'] in question:
                    idx = question.index(chunk['chunk'])
                results.append({'surface': [idx, idx + len(chunk['chunk'])], 'uris': candidate_items})
        return results

    def link_entities_relations(self, question, chunks=None):
        return {"relations": self.link_relations(question, chunks),
                "entities": self.link_entities(question, chunks)}

    def search(self, term):
        try:
            term = term.replace('\r\n', '').replace('?', '')
            if len(term) <= 2:
                return
            query = " ".join(self.n_grams(term))
            hits = self.indexer.search(query, field='ngram')
            # print len(hits)
            for hit in hits:  # hits support mapping interface
                yield hit['uri'].replace('\r\n', '')
        except Exception as err:
            print err
            self.q += 1
            return

    def create_index(self, input_file_path, n=3):
        directory = store.FSDirectory.open(File(self.index_path).toPath())
        analyzer = analysis.standard.StandardAnalyzer()
        indexer = engine.Indexer(directory=directory, analyzer=analyzer)
        indexer.set('term', engine.Field.Text, stored=True)
        indexer.set('uri', engine.Field.Text, stored=True)
        indexer.set('ngram', engine.Field.Text, stored=True)

        with open(input_file_path, 'r') as input_file:
            for line in tqdm(input_file):
                uri = line.lower()
                name = uri[line.rindex('/') + 1:]
                indexer.add(term=name, uri=uri, ngram=self.n_grams(name, n))
            indexer.commit()

    def n_grams(self, term, n=3):
        for i in range(len(term) - n + 1):
            yield term[i:i + n]


if __name__ == '__main__':
    # print list(linker.n_grams('this is a test', 3))
    linker = LuceneLinker(index_path='../../../output/index/',
                          input_file_path='../../../data/dbpedia/earl_properties.txt',
                          create_index=False)
    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    parser = argparse.ArgumentParser(description='Generate linker output')
    parser.add_argument("--base_path", help="base path", default="../../../", dest="base_path")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument('--path', help='input dataset', default='data/LC-QuAD/linked2843.json', dest='ds_path')
    parser.add_argument('--output', help='output path', default='data/LC-QuAD/ngram_linker_classifier_chunker.json',
                        dest='output_path')
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked_IOB.pk",
                        dest="gold_chunk")
    args = parser.parse_args()

    ds = LC_Qaud_Linked(os.path.join(args.base_path, args.ds_path))

    with open(os.path.join(args.base_path, args.gold_chunk)) as data_file:
        gold_chunk_dataset = pk.load(data_file)
    # chunker = GoldChunker({item[0]: item[1:] for item in gold_chunk_dataset})

    chunker = ClassifierChunkParser([], os.path.join(args.base_path, args.model))
    # chunker = SENNAChunker()

    results = []
    for qapair in tqdm(ds.qapairs):
        chunks = chunker.get_phrases(qapair.question.raw_question)
        result = {'entities': [], 'relations': [], 'question': qapair.question.raw_question}
        relations = []
        for chunk in chunks:
            if chunk['class'] == 'relation':
                uris = []
                idx = 0
                for item in linker.search(chunk['chunk']):
                    uris.append({'confidence': 0.1, 'uri': item})
                    idx += 1
                    if idx > 10:
                        break
                relations.append({'surface': [0, 0], 'uris': uris})
        result['relations'] = relations
        results.append(result)
    print linker.q
    with open(os.path.join(args.base_path, args.output_path), 'w') as data_file:
        json.dump(results, data_file)

    # earl = EARL(os.path.join(args.base_path, args.output_path))
    # print earl.do(ds.qapairs[0])
