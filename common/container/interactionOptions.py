from common.container.interactionOption import InteractionOption
from common.utility.uniqueList import UniqueList
import itertools
import math


class InteractionOptions:
    def __init__(self, complete_interpretation_space, parser):
        self.dic = dict()
        self.complete_interpretation_space = complete_interpretation_space
        self.all_queries = UniqueList()
        self.all_ios = UniqueList()
        for output in complete_interpretation_space:
            for query in output["queries"]:
                query["removed"] = False
                self.all_queries.addIfNotExists(query)
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

        self.__remove_items_contained_in_others()
        self.__remove_single_options()

        for item in self.dic:
            for io in self.dic[item]:
                self.all_ios.addIfNotExists(io)

    def __remove_single_options(self):
        # Remove items that have no alternatives
        self.dic = {item: self.dic[item] for item in self.dic if len(self.dic[item]) > 1}

    def __remove_items_contained_in_others(self):
        # Remove items with surface contained in other items
        idxs = [map(int, item.strip("[]").split(", ")) for item in self.dic if item != "type"]
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

    def add(self, interactionOption):
        if interactionOption.id in self.dic:
            result = self.dic[interactionOption.id].addIfNotExists(interactionOption)
            if result != interactionOption:
                if isinstance(result.value, dict) and isinstance(interactionOption.value, dict):
                    result.value["confidence"] = max(result.value["confidence"], interactionOption.value["confidence"])
                if isinstance(interactionOption, InteractionOption):
                    result.addQuery(interactionOption.related_queries)
        else:
            self.dic[interactionOption.id] = UniqueList([interactionOption])

    def all_active_queries(self):
        return [query for query in self.all_queries if not query["removed"]]

    def all_active_ios(self):
        return [io for io in self.all_ios if not io.removed()]

    def filter_interpretation_space(self, interaction_option):
        positive = [query for query in interaction_option.related_queries if not query["removed"]]
        negetive = [query for query in self.all_active_queries() if query not in positive]

        return positive, negetive

    def entropy(self, interpretation_space, s=None):
        if s is None:
            s = sum([q['complete_confidence'] for q in interpretation_space])
        plogs = []
        for query in interpretation_space:
            p = float(query['complete_confidence']) / s
            plogs.append(p * math.log(p, 2))
        return -sum(plogs)

    def averageEntropy(self, interaction_option):
        S_sum = sum([q['complete_confidence'] for q in self.all_active_queries()])
        queries_contain_io, queries_not_contain_io = self.filter_interpretation_space(interaction_option)
        entropy_positive = self.entropy(queries_contain_io, S_sum)
        entropy_negetive = self.entropy(queries_not_contain_io, S_sum)
        p_entropy_positive = sum([q['complete_confidence'] for q in queries_contain_io]) / S_sum
        p_entropy_negetive = sum([q['complete_confidence'] for q in queries_not_contain_io]) / S_sum

        return p_entropy_positive * entropy_positive + p_entropy_negetive * entropy_negetive

    def interactionWithMaxInformationGain(self):
        entropy = self.entropy(self.all_active_queries())
        information_gains = []

        for io in self.all_active_ios():
            information_gains.append(entropy - self.averageEntropy(io))

        io, idx = max([(v, i) for i, v in enumerate(information_gains)])
        print self.all_active_ios()[idx].value
        return idx

    def has_interaction(self):
        return len(self.all_active_ios()) > 1

    def update(self, io_idx, value):
        io = self.all_active_ios()[io_idx]
        queries_contain_io, queries_not_contain_io = self.filter_interpretation_space(io)
        if value:
            for query in queries_not_contain_io:
                query["removed"] = True
        else:
            io.set_remove(True)
            for query in queries_contain_io:
                query["removed"] = True

        io.set_removed(True)
        # remove IOs which have no active query
        for io in self.all_active_ios():
            if not io.removed():
                io.set_removed(all([query["removed"] for query in io.related_queries]))

    def __iter__(self):
        for item in self.dic:
            yield item
