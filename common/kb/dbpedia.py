from common.utility.utils import Utils
from common.utility.cacheDict import CacheDict
import config
import requests
import urllib
import os


class DBpedia:
    def __init__(self, endpoint=config.config['general']['dbpedia']['endpoint'],
                 wikidata_endpoint=config.config['general']['wikidata']['endpoint'], use_cache=False, cache_path=None):
        self.endpoint = endpoint
        self.wikidata_endpoint = wikidata_endpoint
        self.cache_path = cache_path
        self.use_cache = use_cache
        self.type_cache = {}
        self.label_abstract_cache = {}
        self.wikidata_cache = {}
        self.example_triples_cache = {}

        if self.use_cache:
            Utils.makedirs(cache_path)
            self.type_cache = CacheDict(os.path.join(cache_path, 'types.cache'))
            self.label_abstract_cache = CacheDict(os.path.join(cache_path, 'label_abstract.cache'))
            self.wikidata_cache = CacheDict(os.path.join(cache_path, 'wikidata.cache'))
            self.example_triples_cache = CacheDict(os.path.join(cache_path, 'example_triples.cache'))

    def query(self, q):
        payload = (
            ('query', q),
            ('format', 'application/json'))
        try:
            r = requests.get(self.endpoint, params=payload, timeout=60)
        except:
            return 0, None

        return r.status_code, r.json() if r.status_code == 200 else None

    def get_types(self, uri):
        if not self.use_cache or uri not in self.type_cache:
            query = '''SELECT * WHERE {{<{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?t. 
            ?t <http://www.w3.org/2000/01/rdf-schema#subClassOf>* ?t2. 
            FILTER ( strstarts(str(?t), "http://dbpedia.org/ontology/"))}}'''.format(
                uri.encode("ascii", "ignore"))
            payload = {'query': query, 'format': 'application/json'}
            results = Utils.call_web_api(self.endpoint + '?' + urllib.urlencode(payload), None)
            if results is None:
                return []
            self.type_cache[uri] = list(set(
                [item['t']['value'] for item in results['results']['bindings']] + [item['t2']['value'] for item in
                                                                                   results['results']['bindings']]))
        return self.type_cache[uri]

    def get_label_abstract(self, uri):
        if not self.use_cache or uri not in self.label_abstract_cache:
            query = '''SELECT DISTINCT ?label, SUBSTR(?abstract,1,200) where {{ 
<{0}> <http://www.w3.org/2000/01/rdf-schema#label> ?label.
OPTIONAL {{ <{0}> <http://dbpedia.org/ontology/abstract> ?abstract FILTER (lang(?abstract) = 'en')}}
FILTER (lang(?label) = 'en')  }}'''.format(uri.encode("ascii", "ignore"))
            payload = {'query': query, 'format': 'application/json'}
            results = Utils.call_web_api(self.endpoint + '?' + urllib.urlencode(payload), None)

            label = uri[uri.rindex('/') + 1:]
            try:
                label = results['results']['bindings'][0]['label']['value']
            except:
                pass
            abstract = ''
            try:
                abstract = results['results']['bindings'][0]['abstract']['value']
            except:
                pass

            self.label_abstract_cache[uri] = [label, abstract]
        return self.label_abstract_cache[uri]

    def get_wikidata_description(self, uri):
        if not self.use_cache or uri not in self.wikidata_cache:
            # http://www.w3.org/2000/01/rdf-schema#comment
            if 'ontology/' in uri:
                owl_str = 'equivalentClass'
            elif 'property/' in uri:
                owl_str = 'equivalentProperty'
            else:
                owl_str = 'sameAs'
            query = '''SELECT DISTINCT * WHERE {{ <{0}> <http://www.w3.org/2002/07/owl#{1}> ?a 
            FILTER regex(?a,'wikidata.org','i') }} LIMIT 1'''.format(uri.encode("ascii", "ignore"), owl_str)
            payload = {'query': query, 'format': 'application/json'}
            results = Utils.call_web_api(self.endpoint + '?' + urllib.urlencode(payload), None)

            if len(results['results']['bindings']) == 0:
                self.wikidata_cache[uri] = ''
            else:
                wikidata_id = results['results']['bindings'][0]['a']['value']
                query = '''SELECT * WHERE {{ <{0}> <http://schema.org/description> ?b FILTER(lang(?b) = 'en' )}}'''.format(
                    wikidata_id)
                payload = {'query': query, 'format': 'json'}
                results = Utils.call_web_api(self.wikidata_endpoint + '?' + urllib.urlencode(payload),
                                             None)
                description = ''
                try:
                    description = results['results']['bindings'][0]['b']['value']
                except:
                    pass

                self.wikidata_cache[uri] = description
        return self.wikidata_cache[uri]

    def get_example_triples(self, uri):
        if 'ontology/' in uri or 'property/' in uri:
            if not self.use_cache or uri not in self.example_triples_cache:
                query = '''SELECT DISTINCT ?a ?b  where {{ ?a <{0}> ?b 
                FILTER strstarts(str(?a), "http://dbpedia.org/") 
                FILTER strstarts(str(?b), "http://dbpedia.org/") 
                }} LIMIT 2'''.format(
                    uri.encode("ascii", "ignore"))
                payload = {'query': query, 'format': 'application/json'}
                results = Utils.call_web_api(self.endpoint + '?' + urllib.urlencode(payload), None)

                if len(results['results']['bindings']) == 0:
                    self.example_triples_cache[uri] = []
                else:
                    output = []
                    for item in results['results']['bindings']:
                        output.append([item['a']['value'], item['b']['value']])

                    self.example_triples_cache[uri] = output
            return self.example_triples_cache[uri]
        return []

    @staticmethod
    def parse_uri(input_uri):
        if isinstance(input_uri, bool):
            return 'bool', input_uri
        raw_uri = input_uri.strip('<>')
        if raw_uri.find('/resource/') >= 0:
            return '?s', raw_uri
        elif raw_uri.find('/ontology/') >= 0 or raw_uri.find('/property/') >= 0:
            return '?p', raw_uri
        elif raw_uri.find('rdf-syntax-ns#type') >= 0:
            return '?t', raw_uri
        elif raw_uri.startswith('?'):
            return 'g', raw_uri
        else:
            return '?u', raw_uri

    @staticmethod
    def uri_to_sparql(input_uri):
        if input_uri.uri_type == 'g':
            return input_uri.uri
        return u'<{}>'.format(input_uri.uri)
