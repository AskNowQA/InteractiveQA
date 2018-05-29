from common.utility.utils import Utils
import config
import requests
import urllib
import os
import json


class DBpedia:
    def __init__(self, endpoint=config.config['general']['dbpedia']['endpoint'], use_cache=False, cache_path=None):
        self.endpoint = endpoint
        self.cache_path = cache_path
        self.use_cache = use_cache
        self.cache = {}
        if self.use_cache:
            Utils.makedirs(cache_path)
            self.cache_path = os.path.join(cache_path, 'types.cache')
            self.__load_cache()

    def query(self, q):
        payload = (
            ('query', q),
            ('format', 'application/json'))
        try:
            r = requests.get(self.endpoint, params=payload, timeout=60)
        except:
            return 0, None

        return r.status_code, r.json() if r.status_code == 200 else None

    def __load_cache(self):
        try:
            with open(self.cache_path) as cache_file:
                self.cache = json.load(cache_file)
        except:
            self.cache = {}

    def __save_cache(self):
        try:
            with open(self.cache_path, 'w') as cache_file:
                json.dump(self.cache, cache_file)
            return True
        except:
            return False

    def get_types(self, uri):
        if uri not in self.cache or not self.use_cache:
            query = 'SELECT ?t WHERE {{<{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?t}}'.format(
                uri.encode("ascii", "ignore"))
            payload = {'query': query, 'format': 'application/json'}
            results = Utils.call_web_api(self.endpoint + '?' + urllib.urlencode(payload), None)

            self.cache[uri] = [item['t']['value'] for item in results['qa_results']['bindings'] if
                               'yago' not in item['t']['value']]
            self.__save_cache()
        return self.cache[uri]

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
