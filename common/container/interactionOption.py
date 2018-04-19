import math


class InteractionOption:
    def __init__(self, id, value, query):
        self.id = id
        self.value = value
        self.related_queries = [query]

    def addQuery(self, query):
        self.related_queries.extend(query)

    def probability(self):
        confidences = [query['complete_confidence'] for query in self.related_queries]
        return sum(confidences) / len(confidences)

    def __eq__(self, other):
        if isinstance(other, InteractionOption):
            return self.id == other.id and self.value == other.value
        raise NotImplemented
