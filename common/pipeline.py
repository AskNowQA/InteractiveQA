from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.goldChunker import GoldChunker
from common.component.linker.earl import EARL
from common.component.linker.falcon import Falcon
from common.component.linker.mdp import MDP
from common.component.linker.compositeLinker import CompositeLinker
from common.component.linker.rnliwod import RNLIWOD
from common.component.linker.tagme import TagMe
from common.component.linker.luceneLinker import LuceneLinker
from common.component.query.sqg import SQG
from common.utility.uniqueList import UniqueList
from common.container.linkeditem import LinkedItem
from common.utility.utils import Utils

import pickle as pk
import os
import threading
import itertools
import copy
import datetime
import queue as Queue
import re


class IQAPipeline:
    def __init__(self, args, kb, parse_sparql):
        self.kb = kb
        self.parse_sparql = parse_sparql

        mdp = MDP(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=True)

        self.__chunkers = []
        if 'senna' in args.chunkers:
            SENNA_chunker = SENNAChunker()
            self.__chunkers.append(SENNA_chunker)
        if 'classifier' in args.chunkers:
            classifier_chunker = ClassifierChunkParser([], os.path.join(args.base_path, args.model))
            self.__chunkers.append(classifier_chunker)
        if 'gold' in args.chunkers:
            if hasattr(args, 'gold_chunk'):
                with open(os.path.join(args.base_path, args.gold_chunk), 'rb') as data_file:
                    gold_chunk_dataset = pk.load(data_file)
                gold_Chunker = GoldChunker({item[0]: item[1:] for item in gold_chunk_dataset})
            self.__chunkers.append(gold_Chunker)
        if 'mdp' in args.chunkers:
            self.__chunkers.append(mdp)

        # Init linkers
        self.__linkers = []
        entity_linkers = []
        relation_linkers = []

        if 'earl' in args.linkers:
            earl = EARL(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=True)
            entity_linkers.append(earl)
            relation_linkers.append(earl)

        if 'falcon' in args.linkers:
            falcon = Falcon(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=True)
            entity_linkers.append(falcon)
            relation_linkers.append(falcon)

        if 'mdp' in args.linkers:
            entity_linkers.append(mdp)
            relation_linkers.append(mdp)
            mdp_connecting_relation = MDP(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=False,
                                          connecting_relation=True, k=20)
            relation_linkers.append(mdp_connecting_relation)
            mdp_connecting_relations = MDP(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=False,
                                           connecting_relations=True)
            relation_linkers.append(mdp_connecting_relations)
            mdp_free_relation_match = MDP(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=False,
                                          free_relation_match=True)
            relation_linkers.append(mdp_free_relation_match)

        # entity_linkers.append(LuceneLinker(index='idx_ent_ngram', use_ngram=True))
        # entity_linkers.append(LuceneLinker(index='idx_ent'))
        # relation_linkers.append(LuceneLinker(index='idx_rel_ngram', use_ngram=True))
        # relation_linkers.append(LuceneLinker(index='idx_rel_stemmer', use_stemmer=True))

        # if hasattr(args, 'dataset') and args.dataset == 'lcquad':
        #     relation_linkers.append(RNLIWOD(os.path.join(args.base_path, 'data/LC-QuAD/relnliodLogs'),
        #                                     dataset_path=os.path.join(args.base_path, 'data/LC-QuAD/linked_3200.json')))
        #     entity_linkers.append(TagMe(os.path.join(args.base_path, 'data/LC-QuAD/tagmeNEDLogs'),
        #                                 dataset_path=os.path.join(args.base_path, 'data/LC-QuAD/linked_3200.json')))

        for entity_linker in entity_linkers:
            for relation_linker in relation_linkers:
                self.__linkers.append(CompositeLinker(entity_linker=entity_linker, relation_linker=relation_linker))

        # Init query builders
        sqg = SQG()
        self.__query_builders = [sqg]

        self.pipelines = []
        for chunker in self.__chunkers:
            for linker in self.__linkers:
                for qb in self.__query_builders:
                    self.pipelines.append((chunker, linker, qb))
        self.components = [self.__chunk, self.__link, self.__build_query]
        self.qapair = None

    def __check_linkers(self, entities=[], relations=[]):
        if self.qapair is not None:
            wrong_ent = True
            wrong_rel = True
            if len(entities) == len([uri_o for uri_o in self.qapair.sparql.uris if uri_o.is_entity()]):
                wrong_ent = len(
                    [uri_o for uri_o in self.qapair.sparql.uris if
                     uri_o.is_entity() and uri_o.uri not in [uri['uri'] for item in entities for uri in
                                                             item['uris']]]) > 0
            # if len(relations) == len([uri_o for uri_o in self.qapair.sparql.uris if uri_o.is_ontology()]):
            #     wrong_rel = len(
            #         [uri_o for uri_o in self.qapair.sparql.uris if
            #          uri_o.is_ontology() and uri_o.uri not in [uri['uri'] for item in relations for uri in
            #                                                    item['uris']]]) > 0
            type_uri = None
            if '#type' in self.qapair.sparql.raw_query:
                type_uri = \
                    re.findall('(<[^>]*>|\?[^ ]*)',
                               self.qapair.sparql.raw_query[self.qapair.sparql.raw_query.index('#type'):])[0]
                target_rels = [uri_o for uri_o in self.qapair.sparql.uris if
                               uri_o.is_ontology() and uri_o.raw_uri != type_uri]
            else:
                target_rels = [uri_o for uri_o in self.qapair.sparql.uris if uri_o.is_ontology()]
            if type_uri is None:
                if len(relations) != len([uri_o for uri_o in self.qapair.sparql.uris if uri_o.is_ontology()]):
                    return False
            if len(relations) > len([uri_o for uri_o in self.qapair.sparql.uris if uri_o.is_ontology()]):
                return False

            wrong_rel = len(
                [uri_o for uri_o in target_rels if uri_o.uri not in [uri['uri'] for item in relations for uri in
                                                                     item['uris']]]) > 0
            return not (wrong_ent or wrong_rel)
        return True

    def __build_query(self, prev_output, __query_builders):
        outputs = [qb.build_query(prev_output['question'], prev_output['entities'], prev_output['relations'],
                                  'boolean' in self.qapair.sparql.query_features(),
                                  'count' in self.qapair.sparql.query_features()) for qb in
                   __query_builders if self.__check_linkers(prev_output['entities'], prev_output['relations'])]
        # outputs = [{'queries': [{
        #     'query': self.qapair.sparql.raw_query,
        #     'confidence': 1.0,
        #     'type_confidence': 1.0,
        #     'type': 'list'}]} for qb in
        #     __query_builders if self.__check_linkers(prev_output['entities'], prev_output['relations'])]
        # outputs = [item for item in outputs if len(item['queries']) > 0]
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
                                added_item = output[linked_item_type].add_if_not_exists(linked_item)
                                if added_item != linked_item:
                                    added_item.related_queries.add_if_not_exists(query)
                                linked_items_confidence *= uri.confidence
                                found = True
                                break
                        if found:
                            break
                query['complete_confidence'] = linked_items_confidence * query['confidence'] * query['type_confidence']
        return outputs

    def __link(self, prev_output, __linkers):
        chunks = prev_output['chunks']

        # outputs = Utils.run_in_parallel([prev_output['question'], chunks],
        #                                 *[item.link_entities_relations for item in self.__linkers])
        outputs = [item.link_entities_relations(prev_output['question'], chunks) for item in __linkers]

        for item in outputs:
            if len(item['entities']) > 2:
                pass
        # outputs = [item  and len(item['relations']) <= 3]

        # According to LC-QuAD specs, there is no query with more than two entities or three relations
        outputs = [item for item in outputs if len(item['entities']) <= 2 and len(item['relations']) <= 3]

        for item in outputs:
            item['question'] = prev_output['question']
            item['chunks'] = prev_output['chunks']

        combinations = []
        outputs_len = len(outputs)
        for i in range(outputs_len):
            for j in range(i + 1, outputs_len):
                combinations.extend(self.__merge_linkers(outputs[i], outputs[j]))
        outputs.extend(combinations)

        # remove one of the relations
        # for item in outputs:
        #     if len(item['relations']) > 1:
        #         for idx in range(len(item['relations'])):
        #             new_item = copy.deepcopy(item)
        #             new_item['relations'].pop(idx)
        #             outputs.append(new_item)

        # to_be_deleted = []
        # for idx1 in range(len(outputs)):
        #     for idx2 in range(idx1, len(outputs)):
        #         item1 = outputs[idx1]
        #         item2 = outputs[idx2]
        #
        #         if item1['entities']

        return outputs

    def __merge_linkers(self, links1, links2):
        outputs = []
        for link_type in ['entities', 'relations']:
            if links1[link_type] == links2[link_type]:
                pass
            else:
                for item2 in links2[link_type]:
                    if item2['surface'] == [0, 0]:
                        for idx in range(len(links1[link_type])):
                            new_output = copy.deepcopy(links1)
                            new_output[link_type][idx]['uris'].extend(item2['uris'])
                            outputs.append(new_output)
                        new_output = copy.deepcopy(links1)
                        new_output[link_type].append(item2)
                        outputs.append(new_output)

                # Combine links with the same surface form
                for idx1 in range(len(links1[link_type])):
                    item1 = links1[link_type][idx1]
                    for item2 in links2[link_type]:
                        if item1['surface'] == item2['surface']:
                            new_output = copy.deepcopy(links1)
                            existing_uris = [item['uri'] for item in new_output[link_type][idx1]['uris']]
                            for uri in item2['uris']:
                                if uri['uri'] not in existing_uris:
                                    new_output[link_type][idx1]['uris'].append(uri)

                            outputs.append(new_output)
        return outputs

    def __chunk(self, question, __chunkers):
        # chunkers_output = Utils.run_in_parallel([question], *[item.get_phrases for item in self.__chunkers])
        chunkers_output = [chunker.get_phrases(question) for chunker in __chunkers]

        # According to LC-QuAD specs, there is no query with more than two entities or three relations
        # for chunks in chunkers_output:
        #     number_of_entities = len([item for item in chunks if item['class'] == 'entity'])
        #     number_of_relations = len([item for item in chunks if item['class'] == 'relation'])
        #     if number_of_entities > 2:
        #         for i in range(number_of_entities - 2):
        #             pass
        #     if number_of_relations > 3:
        #         pass

        return [{'question': question, 'chunks': item} for item in chunkers_output]

    def run(self, qapair):
        self.qapair = qapair
        for uri in qapair.sparql.uris:
            if uri.is_entity():
                uri.types = self.kb.get_types(uri.uri)

        threads = []
        outputs = Queue.Queue()
        done = Queue.Queue()

        def run_pipeline(pipeline):
            # print('start pipeline')
            question = re.sub(r'[^\w+]', ' ', qapair.question.text).replace('TV', 'television').replace(' tv ',
                                                                                                        ' television ')
            output = {-1: [question]}
            for cmpnt_idx, component in enumerate(self.components):
                output[cmpnt_idx] = []
                for prev_output in output[cmpnt_idx - 1]:
                    output[cmpnt_idx].extend(component(prev_output, [pipeline[cmpnt_idx]]))
            # if len(output[2]) > 0:
            outputs.put(output)
            done.put(0)
            # print(datetime.datetime.now(), len(output[2]) > 0)

        for pipeline in self.pipelines:
            run_pipeline(pipeline)
            # t = threading.Thread(target=run_pipeline, args=(pipeline,))
            # t.start()
            # threads.append(t)

        # for t in threads:
        #     t.join()

        return outputs, done, len(self.pipelines)
