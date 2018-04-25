class Oracle:
    def __init__(self):
        pass

    def answer(self, qapair, io):
        if io.value == 'boolean':
            return "ask " in qapair.sparql.query.lower()
        elif io.value == 'count':
            return "count(" in qapair.sparql.query.lower()
        elif io.value == 'list':
            return not ("ask " in qapair.sparql.query.lower() or "count(" in qapair.sparql.query.lower())
        elif io.value['type'] == 'linked':
            return len([uri.uri for uri in qapair.sparql.uris if uri.uri == io.value["uri"]]) > 0
        elif io.value['type'] == 'type':
            return len([uri for uri in qapair.sparql.uris if uri.is_entity() and io.value["uri"] in uri.types]) > 0
        else:
            return False
