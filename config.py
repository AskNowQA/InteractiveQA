config = {
    'IQA': {
        'backend': 'http://127.0.0.1:5002'
    },
    'general': {
        'http': {
            'timeout': 120
        },
        'dbpedia': {
            # 'endpoint': 'http://dbpedia.org/sparql'
            'endpoint': 'http://131.220.9.219:8164/sparql'
        },
        'wikidata': {
            'endpoint': 'https://query.wikidata.org/sparql'
        }
    },
    'semweb2nl': {
        'endpoint': 'http://127.0.0.1:8680/semweb2nl/'
    },
    'EARL': {
        'endpoint': 'http://sda-srv02.iai.uni-bonn.de:4999/processQuery'
    },
    'SQG': {
        # 'endpoint': 'http://sda-srv02.iai.uni-bonn.de:5000/qg/api/v1.0/query',
        'endpoint': 'http://localhost:5010/qg/api/v1.0/query',
        'timeout': 120,
        'use_sqg_cache': True
    }
}
