class Oracle:
    def __init__(self):
        pass

    def answer(self, qapair, io):
        if io.value['type'] == 'linked':
            return len([uri.uri for uri in qapair.sparql.uris if uri.uri == io.value["uri"]]) > 0
        else:
            return len([uri for uri in qapair.sparql.uris if uri.is_entity() and io.value["uri"] in uri.types]) > 0
