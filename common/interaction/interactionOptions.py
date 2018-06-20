from common.interaction.interactionOption import InteractionOption
from common.utility.uniqueList import UniqueList
from common.kb.dbpedia import DBpedia
from common.container.linkeditem import LinkedItem
from common.container.uri import Uri
from common.container.sparql import SPARQL
import math


class InteractionOptions:
    def __init__(self, complete_interpretation_space, uri_parser=None, sparql_parser=None, kb=DBpedia(), c2=True,
                 c3=True):
        self.dic = dict()
        self.sparql_parser = sparql_parser
        self.kb = kb
        # self.complete_interpretation_space = complete_interpretation_space
        self.all_queries = UniqueList()
        self.all_ios = UniqueList()
        for output in complete_interpretation_space:
            for linked_item_type in ['entities', 'relations']:
                if linked_item_type in output:
                    for item in output[linked_item_type]:
                        io = InteractionOption(item.surface_form, item, [], 'linked')
                        self.add(io)

            if 'queries' in output:
                for query in output['queries']:
                    query['removed'] = False
                    self.all_queries.add_or_update(query, eq_func=lambda x, y: x['query'] == y['query'],
                                                   opt_func=lambda x, y: x if x['complete_confidence'] > y[
                                                       'complete_confidence'] else y)
                    if c3:
                        self.add(InteractionOption('type', query['type'], query, 'type'))

        for item in self.dic:
            for io in self.dic[item]:
                if io.type == 'linked':
                    io.addQuery(self.__related_queries(io.value.uris[0]))

        if c2:
            for item in self.dic:
                for io in self.dic[item]:
                    if io.type == 'linked' and isinstance(io.value, LinkedItem) and io.value.uris[0].is_entity():
                        for type in kb.get_types(io.value.uris[0].uri):
                            self.add(InteractionOption(io.id, LinkedItem(io.id, [Uri(type, uri_parser)]),
                                                       io.related_queries,
                                                       'linked_type'))

        self.__remove_items_contained_in_others()
        # there are cases where an entity is used in one query and not in others, thus can't simply remove it.
        # self.__remove_single_options()

        for item in self.dic:
            for io in self.dic[item]:
                self.all_ios.add_if_not_exists(io)

    def __related_queries(self, uri):
        for query in self.all_queries:
            if uri.uri in query['query']:
                yield query

    def __remove_single_options(self):
        # Remove items that have no alternatives
        self.dic = {item: self.dic[item] for item in self.dic if len(self.dic[item]) > 1}

    def __remove_items_contained_in_others(self):
        try:
            # Remove items with surface contained in other items
            idxs = [map(int, item.strip('[]').split(', ')) for item in self.dic if item != 'type']
            ranges = [[item[0], item[0] + item[1]] for item in idxs]
            contained = []
            for x in ranges:
                contained += [[y[0], y[1] - y[0], x[0], x[1] - x[0]] for y in ranges if
                              (x[0] >= y[0] and x[1] <= y[1]) and (x[0] != y[0] or x[1] != y[1])]
            for item in contained:
                tmp = self.dic[str(item[:2])]
                del self.dic[str(item[:2])]
                for io in tmp:
                    io.id = str(item[2:])
                    self.add(io)
        except:
            pass

    def add(self, interactionOption):
        if interactionOption.id in self.dic:
            result = self.dic[interactionOption.id].add_if_not_exists(interactionOption)
            if result != interactionOption:
                if isinstance(interactionOption, InteractionOption):
                    result.addQuery(interactionOption.related_queries)
                    if isinstance(result.value, dict) and isinstance(interactionOption.value, dict):
                        result.value['confidence'] = max(result.value['confidence'],
                                                         interactionOption.value['confidence'])
        else:
            self.dic[interactionOption.id] = UniqueList([interactionOption])

    def __all_active_queries(self):
        return [query for query in self.all_queries if not query['removed']]

    def __all_active_ios(self):
        return [io for io in self.all_ios if not io.removed()]

    def __filter_interpretation_space(self, interaction_option):
        # positive = [query for query in interaction_option.related_queries if not query['removed']]
        positive = [query for query in self.__all_active_queries() if
                    not query['removed'] and query in interaction_option.related_queries]
        negative = [query for query in self.__all_active_queries() if query not in positive]

        return positive, negative

    def __entropy(self, interpretation_space, s=None):
        if s is None:
            s = sum([q['complete_confidence'] for q in interpretation_space])
        plogs = []
        for query in interpretation_space:
            if s == 0:
                p = 0
            else:
                p = query['complete_confidence'] / s

            if p == 0:
                plogs.append(0)
            else:
                plogs.append(p * math.log(p, 2))
        return -sum(plogs)

    def __averageEntropy(self, interaction_option):
        S_sum = sum([q['complete_confidence'] for q in self.__all_active_queries()])
        queries_contain_io, queries_not_contain_io = self.__filter_interpretation_space(interaction_option)
        entropy_positive = self.__entropy(queries_contain_io, S_sum)
        entropy_negative = self.__entropy(queries_not_contain_io, S_sum)
        if S_sum == 0:
            p_entropy_positive = 0
            p_entropy_negative = 0
        else:
            p_entropy_positive = sum([q['complete_confidence'] for q in queries_contain_io]) / S_sum
            p_entropy_negative = sum([q['complete_confidence'] for q in queries_not_contain_io]) / S_sum

        return p_entropy_positive * entropy_positive + p_entropy_negative * entropy_negative

    def __informationGain(self):
        entropy = self.__entropy(self.__all_active_queries())
        information_gains = []

        for io in self.__all_active_ios():
            information_gains.append([io, entropy - self.__averageEntropy(io)])

        return information_gains

    def interaction_with_max_information_gain(self):
        information_gains = [item[1] for item in self.__informationGain()]
        io, idx = max([(v, i) for i, v in enumerate(information_gains)])
        return self.__all_active_ios()[idx]

    def interaction_with_max_option_gain(self, w):
        information_gains = self.__informationGain()
        option_gains = [math.pow(item[0].usability(), w) * item[1] for item in information_gains]
        io, idx = max([(v, i) for i, v in enumerate(option_gains)])
        return self.__all_active_ios()[idx]

    def interaction_with_max_probability(self):
        S_sum = sum([q['complete_confidence'] for q in self.__all_active_queries()])
        probabilities = []

        for io in self.__all_active_ios():
            p = 0
            for query in io.related_queries:
                if S_sum == 0:
                    p = 0
                else:
                    p += query['complete_confidence'] / S_sum
            probabilities.append(p)

        io, idx = max([(v, i) for i, v in enumerate(probabilities)])
        return self.__all_active_ios()[idx]

    def ranked_queries(self):
        return sorted(self.__all_active_queries(), key=lambda x: x['complete_confidence'], reverse=True)

    def query_with_max_probability(self):
        queries = self.ranked_queries()
        if queries is None or len(queries) == 0:
            return None
        return SPARQL(queries[0]['query'], self.sparql_parser)

    def has_interaction(self):
        if len(self.__all_active_queries()) > 1 and len(
                set([item['query'] for item in self.__all_active_queries()])) > 1:
            if len(self.__all_active_ios()) > 0:
                information_gains = [item[1] for item in self.__informationGain()]
                return sum(information_gains) > 0
            else:
                return False
        return False

    def update(self, io, value):
        queries_contain_io, queries_not_contain_io = self.__filter_interpretation_space(io)
        if value:
            for query in queries_not_contain_io:
                query['removed'] = True
        else:
            for query in queries_contain_io:
                query['removed'] = True

        # Remove current IO
        io.set_removed(True)
        # remove IOs which have no active query
        for io in self.__all_active_ios():
            if not io.removed():
                io.set_removed(all([query['removed'] for query in io.related_queries]))

    def __iter__(self):
        for item in self.dic:
            yield item
