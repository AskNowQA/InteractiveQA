from common.utility.uniqueList import UniqueList
from common.container.linkeditem import LinkedItem


class InteractionOption:
    def __init__(self, id, value, query, type=None):
        self.id = id
        self.value = value
        if isinstance(query, list):
            self.related_queries = UniqueList(list(query))
        else:
            self.related_queries = UniqueList([query])
        self.__removed = False
        self.type = type

    def addQuery(self, query):
        for item in query:
            self.related_queries.add_if_not_exists(item)

    def probability(self):
        confidences = [query['complete_confidence'] for query in self.related_queries]
        return sum(confidences) / len(confidences)

    def usability(self):
        if self.type == 'query':
            return 0.1
        elif self.type == 'type':
            return 0.9
        elif self.type == 'linked':
            if self.value.uris[0].is_entity():
                return 0.8
            else:
                return 0.5
        elif self.type == 'linked_type':
            return 0.4

        return 0.5

    def set_removed(self, val):
        self.__removed = val

    def removed(self):
        return self.__removed

    def __eq__(self, other):
        if isinstance(other, InteractionOption):
            return self.id == other.id and (
                    (isinstance(self.value, LinkedItem) and
                     isinstance(other.value, LinkedItem) and
                     self.value.uris == other.value.uris)
                    or self.value == other.value)
        raise NotImplemented

    def __str__(self):
        return str(self.value)
