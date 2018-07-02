config = {
    'general': {
        'http': {
            'timeout': 120
        },
        'dbpedia': {
            'endpoint': 'http://sda-srv01.iai.uni-bonn.de:8164/sparql'
        },
        'wikidata': {
            'endpoint': 'https://query.wikidata.org/sparql'
        }
    },
    'EARL': {
        'endpoint': 'http://sda-srv02.iai.uni-bonn.de:4999/processQuery'
    },
    'SQG': {
        'endpoint': 'http://sda-srv02.iai.uni-bonn.de:5000/qg/api/v1.0/query',
        # 'endpoint': 'http://localhost:5001/qg/api/v1.0/query',
        'timeout': 120,
        'use_sqg_cache': True
    }
}
