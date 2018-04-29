from common.utility.utils import Utils
import config
import itertools


class SQG:
    def __init__(self, endpoint=config.config['SQG']['endpoint'], timeout=config.config['SQG']['timeout']):
        self.endpoint = endpoint
        self.timeout = timeout

    def build_query(self, question, entities=[], relations=[]):
        input = {'question': question,
                 'entities': entities,
                 'relations': relations,
                 'timeout': self.timeout,
                 'use_cache': config.config['SQG']['use_sqg_cache'],
                 'force_list': True}

        result_list = Utils.call_web_api(self.endpoint, input)
        input['force_list'] = False
        input['force_bool'] = True
        result_bool = Utils.call_web_api(self.endpoint, input)

        input['force_list'] = False
        input['force_bool'] = False
        input['force_count'] = True
        result_count = Utils.call_web_api(self.endpoint, input)
        result = {'queries': []}
        for queries in itertools.chain([result_list, result_bool, result_count]):
            if queries is None:
                break
            for query in queries['queries']:
                query['type'] = queries['type']
                query['type_confidence'] = queries['type_confidence']
            result['queries'].extend(queries['queries'])

        return result
