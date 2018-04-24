class InteractionOption:
    def __init__(self, id, value, query):
        self.id = id
        self.value = value
        if isinstance(query, list):
            self.related_queries = query
        else:
            self.related_queries = [query]
        self.__removed = False

    def addQuery(self, query):
        self.related_queries.extend(query)

    def probability(self):
        confidences = [query['complete_confidence'] for query in self.related_queries]
        return sum(confidences) / len(confidences)

    def set_removed(self, val):
        self.__removed = val

    def removed(self):
        return self.__removed

    def __eq__(self, other):
        if isinstance(other, InteractionOption):
            return self.id == other.id and (
                    (isinstance(self.value, dict) and isinstance(other.value, dict) and self.value["uri"] ==
                     other.value["uri"])
                    or self.value == other.value)
        raise NotImplemented
