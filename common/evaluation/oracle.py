class Oracle:
    def __init__(self):
        pass

    def validate_query(self, qapair, query):
        return qapair.sparql == query

    def answer(self, qapair, io):
        if io.type == 'query':
            return qapair.sparql == io.value
        elif io.type == 'type':
            if io.value == 'boolean':
                return "ask " in qapair.sparql.query.lower()
            if io.value == 'count':
                return "count(" in qapair.sparql.query.lower()
            if io.value == 'list':
                return not ("ask " in qapair.sparql.query.lower() or "count(" in qapair.sparql.query.lower())
        elif io.type == 'linked':
            io_uri = io.value.uris[0].uri
            return len([uri.uri for uri in qapair.sparql.uris if uri.uri == io_uri]) > 0
        elif io.type == 'linked_type':
            io_uri = io.value.uris[0].uri
            return len([uri for uri in qapair.sparql.uris if
                        uri.is_entity() and (uri.types is not None and io_uri in uri.types)]) > 0
        else:
            return False
