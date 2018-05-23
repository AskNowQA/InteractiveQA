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
import copy


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
        entity_linkers = []
        relation_linkers = []

        earl = EARL(cache_path=os.path.join(args.base_path, 'caches/'), use_cache=True)
        entity_linkers.append(earl)
        relation_linkers.append(earl)

        entity_linkers.append(
            LuceneLinker(index_path=os.path.join(args.base_path, 'output/idx_ent_ngram/'), use_ngram=True))
        relation_linkers.append(
            LuceneLinker(index_path=os.path.join(args.base_path, 'output/idx_rel_ngram/'), use_ngram=True))
        relation_linkers.append(
            LuceneLinker(index_path=os.path.join(args.base_path, 'output/idx_rel_stemmer/'), use_stemmer=True))

        if args.dataset == 'lcquad':
            relation_linkers.append(RNLIWOD(os.path.join(args.base_path, 'data/LC-QuAD/relnliodLogs'),
                                            dataset_path=os.path.join(args.base_path, 'data/LC-QuAD/linked_3200.json')))
            entity_linkers.append(TagMe(os.path.join(args.base_path, 'data/LC-QuAD/tagmeNEDLogs'),
                                        dataset_path=os.path.join(args.base_path, 'data/LC-QuAD/linked_3200.json')))

        for entity_linker in entity_linkers:
            for relation_linker in relation_linkers:
                self.__linkers.append(CompositeLinker(entity_linker=entity_linker, relation_linker=relation_linker))

        # Init query builders
        sqg = SQG()
        self.__query_builders = [sqg]

        self.components = [self.__chunk, self.__link, self.__build_query]
        self.q__qapair = None

    def __check_linkers(self, entities=[], relations=[]):
        if self.q__qapair is not None:
            wrong_ent = len(
                [uri_o for uri_o in self.q__qapair.sparql.uris if
                 uri_o.is_entity() and uri_o.uri not in [uri['uri'] for item in entities for uri in item['uris']]]) > 0
            wrong_rel = len(
                [uri_o for uri_o in self.q__qapair.sparql.uris if
                 uri_o.is_ontology() and uri_o.uri not in [uri['uri'] for item in relations for uri in
                                                           item['uris']]]) > 0
            return not (wrong_ent or wrong_rel)
        return True

    def __build_query(self, prev_output):
        outputs = [qb.build_query(prev_output['question'], prev_output['entities'], prev_output['relations']) for qb in
                   self.__query_builders if self.__check_linkers(prev_output['entities'], prev_output['relations'])]
        outputs = [item for item in outputs if len(item['queries']) > 0]
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

    def __chunk(self, question):
        chunkers_output = [chunker.get_phrases(question) for chunker in self.__chunkers]
        return [{'question': question, 'chunks': item} for item in chunkers_output]

    def run(self, qapair):
        self.q__qapair = qapair
        for uri in qapair.sparql.uris:
            if uri.is_entity():
                uri.types = self.kb.get_types(uri.uri)

        outputs = {-1: [qapair.question.text]}
        for cmpnt_idx, component in enumerate(self.components):
            outputs[cmpnt_idx] = []
            for prev_output in outputs[cmpnt_idx - 1]:
                outputs[cmpnt_idx].extend(component(prev_output))

        return outputs
