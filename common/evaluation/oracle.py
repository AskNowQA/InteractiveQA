class Oracle:
    def __init__(self):
        pass

    def answer(self, qapair, io):
        return len([uri.uri for uri in qapair.sparql.uris if uri.uri == io.value["uri"]]) > 0
