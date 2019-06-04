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
            'endpoint': 'http://sda01dbpedia:softrock@131.220.9.219/sparql'
        },
        'wikidata': {
            'endpoint': 'https://query.wikidata.org/sparql'
        }
    },
    'semweb2nl': {
        'endpoint': 'http://127.0.0.1:8680/semweb2nl/'
    },
    'EARL': {
        'endpoint': 'http://sda.tech/earl/api/processQuery'
    },
    'Falcon': {
        'endpoint': 'https://labs.tib.eu/falcon/api?mode=long'
    },
    'MDP': {
        'endpoint': 'http://localhost:5000/link'
    },
    'SQG': {
        'endpoint': 'http://solide-qa.cs.upb.de:9200/qg/api/v1.0/query',
        # 'endpoint': 'http://localhost:5010/qg/api/v1.0/query',
        'timeout': 120,
        'use_sqg_cache': True
    }
}
