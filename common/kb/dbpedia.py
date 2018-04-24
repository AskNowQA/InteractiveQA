from common.utility.utils import Utils
import config
import urllib


class DBpedia:
    def __init__(self, endpoint=config.config["general"]["dbpedia"]["endpoint"]):
        self.endpoint = endpoint

    def get_types(self, uri):
        query = "SELECT ?t WHERE {{<{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?t}}".format(uri)
        payload = {'query': query, 'format': 'application/json'}

        results = Utils.call_web_api(self.endpoint + "?" + urllib.urlencode(payload), None)
        return [item["t"]["value"] for item in results["results"]["bindings"] if "yago" not in item["t"]["value"]]

    @staticmethod
    def parse_uri(input_uri):
        if isinstance(input_uri, bool):
            return "bool", input_uri
        raw_uri = input_uri.strip("<>")
        if raw_uri.find("/resource/") >= 0:
            return "?s", raw_uri
        elif raw_uri.find("/ontology/") >= 0 or raw_uri.find("/property/") >= 0:
            return "?p", raw_uri
        elif raw_uri.find("rdf-syntax-ns#type") >= 0:
            return "?t", raw_uri
        elif raw_uri.startswith("?"):
            return "g", raw_uri
        else:
            return "?u", raw_uri

    @staticmethod
    def uri_to_sparql(input_uri):
        if input_uri.uri_type == "g":
            return input_uri.uri
        return u"<{}>".format(input_uri.uri)
