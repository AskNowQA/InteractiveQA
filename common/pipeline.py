from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.goldChunker import GoldChunker
from common.component.linker.earl import EARL
from common.component.linker.compositeLinker import CompositeLinker
from common.component.linker.rnliwod import RNLIWOD
from common.component.linker.tagme import TagMe
from common.component.linker.luceneLinker import LuceneLinker
from common.component.query.sqg import SQG
from common.utility.uniqueList import UniqueList
from common.container.linkeditem import LinkedItem

import pickle as pk
import os
import itertools


class IQAPipeline:
    def __init__(self, args, kb, parse_sparql):
        self.kb = kb
        self.parse_sparql = parse_sparql

        # Init chunkers
        classifier_chunker = ClassifierChunkParser([], os.path.join(args.base_path, args.model))
        SENNA_chunker = SENNAChunker()
        with open(os.path.join(args.base_path, args.gold_chunk)) as data_file:
            gold_chunk_dataset = pk.load(data_file)
        gold_Chunker = GoldChunker({item[0]: item[1:] for item in gold_chunk_dataset})
        self.__chunkers = [SENNA_chunker, classifier_chunker]  # gold_Chunker

        # Init linkers
        self.__linkers = []

        earl = EARL(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=True)
        self.__linkers.append(earl)

        luceneLinker_ngram = LuceneLinker(index_path=os.path.join(args.base_path, 'output/index/'), use_ngram=True)
        self.__linkers.append(CompositeLinker(entity_linker=earl, relation_liner=luceneLinker_ngram))

        luceneLinker_stemmer = LuceneLinker(index_path=os.path.join(args.base_path, 'output/index2/'), use_stemmer=True)
        # self.__linkers.append(CompositeLinker(entity_linker=earl, relation_liner=luceneLinker_stemmer))

        if args.dataset == 'lcquad':
            rnliword = RNLIWOD(os.path.join(args.base_path, 'data/LC-QuAD/relnliodLogs'),
                               dataset_path=os.path.join(args.base_path, 'data/LC-QuAD/linked_3200.json'))
            tag_me = TagMe(os.path.join(args.base_path, 'data/LC-QuAD/tagmeNEDLogs'),
                           dataset_path=os.path.join(args.base_path, 'data/LC-QuAD/linked_3200.json'))
            # self.__linkers.append(CompositeLinker(entity_linker=tag_me, relation_liner=earl))
            # self.__linkers.append(CompositeLinker(entity_linker=tag_me, relation_liner=rnliword))
            # self.__linkers.append(CompositeLinker(entity_linker=earl, relation_liner=rnliword))
            # self.__linkers.append(CompositeLinker(entity_linker=tag_me, relation_liner=luceneLinker_ngram))
            # self.__linkers.append(CompositeLinker(entity_linker=tag_me, relation_liner=luceneLinker_stemmer))

        # Init query builders
        sqg = SQG()
        self.__query_builders = [sqg]

        self.components = [self.__chunk, self.__link, self.__build_query]

    def __build_query(self, prev_output):
        outputs = [qb.build_query(prev_output['question'], prev_output['entities'], prev_output['relations']) for qb in
                   self.__query_builders]
        for output in outputs:
            # Keep only the entity/relation that have been used in the query
            output['entities'] = UniqueList()
            output['relations'] = UniqueList()
            output['question'] = prev_output['question']
            output['chunks'] = prev_output['chunks']
            for query in output['queries']:
                _, _, uris = self.parse_sparql(query['query'])
                linked_items_confidence = 1
                for uri in uris:
                    if uri.is_generic():
                        continue
                    raw_uri = uri.raw_uri.strip('<>')
                    found = False
                    for entity_relation in itertools.chain(prev_output['entities'], prev_output['relations']):
                        for linked_uri in entity_relation["uris"]:
                            if linked_uri['uri'] == raw_uri:
                                linked_item_type = 'entities' if '/resource/' in raw_uri else 'relations'
                                uri.confidence = linked_uri['confidence']
                                linked_item = LinkedItem(str(entity_relation['surface']), [uri], UniqueList([query]))
                                added_item = output[linked_item_type].addIfNotExists(linked_item)
                                if added_item != linked_item:
                                    added_item.related_queries.addIfNotExists(query)
                                linked_items_confidence *= uri.confidence
                                found = True
                                break
                        if found:
                            break
                query['complete_confidence'] = linked_items_confidence * query['confidence'] * query['type_confidence']
        return outputs

    def __link(self, prev_output):
        chunks = prev_output['chunks']
        outputs = [item.link_entities_relations(prev_output['question'], chunks) for item in self.__linkers]
        for item in outputs:
            item['question'] = prev_output['question']
            item['chunks'] = prev_output['chunks']
        return outputs

    def __chunk(self, question):
        chunkers_output = [chunker.get_phrases(question) for chunker in self.__chunkers]
        return [{'question': question, 'chunks': item} for item in chunkers_output]

    def run(self, qapair):
        for uri in qapair.sparql.uris:
            if uri.is_entity():
                uri.types = self.kb.get_types(uri.uri)

        outputs = {-1: [qapair.question.text]}
        for cmpnt_idx, component in enumerate(self.components):
            outputs[cmpnt_idx] = []
            for prev_output in outputs[cmpnt_idx - 1]:
                outputs[cmpnt_idx].extend(component(prev_output))

        return outputs
