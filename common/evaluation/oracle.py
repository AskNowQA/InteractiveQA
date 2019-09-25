class Oracle:
    def __init__(self, kb):
        self.kb = kb

    def validate_query(self, qapair, query):
        query_match = qapair.sparql.equals(query, True, True)
        if query_match > 0.99:
            return True
        else:
            # TODO check output
            if query_match > 0.6:
                results_1 = self.kb.query(qapair.sparql.raw_query)
                results_2 = self.kb.query(query.raw_query)
                if results_1 is None or results_2 is None or results_1[1] is None or results_2[1] is None:
                    return False
                head_var_1 = results_1[1]['head']['vars'][0]
                head_var_2 = results_2[1]['head']['vars'][0]
                if 'COUNT' in qapair.sparql.raw_query and 'COUNT' in query.raw_query:
                    return results_1[1]['results']['bindings'][0][head_var_1]['value'] == \
                           results_2[1]['results']['bindings'][0][head_var_2]['value']
                else:
                    results_1 = [item[head_var_1]['value'] for item in results_1[1]['results']['bindings']]
                    results_2 = [item[head_var_2]['value'] for item in results_2[1]['results']['bindings']]
                    max_len = max(len(results_1), len(results_2))
                    intersec_len = len(set(results_2).intersection(set(results_1)))
                    return intersec_len / max_len > 0.9
            return False

    def answer(self, qapair, io):
        if io.type == 'query':
            return self.validate_query(qapair, io.value)
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
