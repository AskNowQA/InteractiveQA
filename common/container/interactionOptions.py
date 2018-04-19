from common.container.interactionOption import InteractionOption
from common.utility.uniqueList import UniqueList
import itertools
import math


class InteractionOptions:
    def __init__(self, complete_interpretation_space, parser):
        self.dic = dict()
        self.complete_interpretation_space = complete_interpretation_space
        self.all_queries = []
        for output in complete_interpretation_space:
            for query in output["queries"]:
                self.all_queries.append(query)
                self.add(InteractionOption("type", output["type"], query))
                _, _, uris = parser(query["query"])
                for uri in uris:
                    if uri.is_generic():
                        continue
                    raw_uri = uri.uri
                    found = False
                    for entity_relation in itertools.chain(output["entities"], output["relations"]):
                        for item in entity_relation["uris"]:
                            if item["uri"] == raw_uri:
                                self.add(InteractionOption(str(entity_relation['surface']), item, query))
                                found = True
                                break
                        if found:
                            break

        self.__remove_single_options()
        self.__remove_items_contained_in_others()

    def __remove_single_options(self):
        # Remove items that have no alternatives
        self.dic = {item: self.dic[item] for item in self.dic if len(self.dic[item]) > 1}

    def __remove_items_contained_in_others(self):
        # Remove items with surface contained in other items
        idxs = [map(int, item.strip("[]").split(", ")) for item in self.dic if item != "type"]
        ranges = [[item[0], item[0] + item[1]] for item in idxs]
        contained = []
        for x in ranges:
            contained += [[y[0], y[1] - y[0]] for y in ranges if
                          (x[0] >= y[0] and x[1] <= y[1]) and (x[0] != y[0] or x[1] != y[1])]
        for item in contained:
            del self.dic[str(item)]

    def add(self, interactionOption):
        if interactionOption.id in self.dic:
            result = self.dic[interactionOption.id].addIfNotExists(interactionOption)
            if result != interactionOption:
                if isinstance(interactionOption, InteractionOption):
                    result.addQuery(interactionOption.related_queries)
        else:
            self.dic[interactionOption.id] = UniqueList([interactionOption])

    def filter_interpretation_space(self, interaction_option):
        positive = interaction_option.related_queries
        negetive = [query for query in self.all_queries if query not in positive]

        return positive, negetive

    def entropy(self, interpretation_space):
        plogs = []
        for query in interpretation_space:
            p = float(query['complete_confidence'])
            plogs.append(-p * math.log(p, 2))
        return sum(plogs)

    def averageEntropy(self, interaction_option):
        queries_contain_io, queries_not_contain_io = self.filter_interpretation_space(interaction_option)
        entropy_positive = self.entropy(queries_contain_io)
        entropy_negetive = self.entropy(queries_not_contain_io)
        S_i = [(len(queries_contain_io), entropy_positive), (len(queries_not_contain_io), entropy_negetive)]
        S_len = len(self.all_queries)

        return sum([1. * item[0] / S_len * item[1] for item in S_i])

    def itemWithMaxInformationGain(self):
        entropy = self.entropy(self.all_queries)
        information_gains = []
        for item in self.dic:
            for io in self.dic[item]:
                information_gains.append(entropy - self.averageEntropy(io))

        return max([(v, i) for i, v in enumerate(information_gains)])

    def __iter__(self):
        for item in self.dic:
            yield item
