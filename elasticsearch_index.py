#this file is used to create index in elasticsearch. Index has various parameters such as stopwords ; synonyms etc. 

import requests
import json

query = {
  "mappings": {
      "patty_index": {
            "properties": {
              "relation": {
                            "type": "string"
                        },
                        "pattern": {
                            "type": "string",
                            "index_options": "docs",
                            "similarity": "BM25",
                            "analyzer" : "synonym"
              }
            }
     }
  },
  "settings": {
      "analysis": {
            "filter": {
                "english_stop": {
                    "type":       "stop",
                    "stopwords":  ["a", "an", "and", "are", "as", "at", "be", 
                                "by", "for", "if", "in", "into", "is", "it", 
                                "of", "on", "or", "such", "that", "the",
                                "their", "then", "there", "these", "they",
                                "this", "to", "was", "will", "with"] 
                },
                "english_keywords": {
                    "type":       "keyword_marker", 
                    "keywords":   [ "in this paper", "has been proposed", "we propose"]
                },            
                "acronym_en_EN": {
                    "type": "pattern_capture",
                    "patterns": ["(?:[a-zA-Z]\\.)+", "((?:[a-zA-Z]\\.)+[a-zA-Z])",
                                  "((?:[a-zA-Z]\\.)+[s]$)", "((?:[a-zA-Z]\\.)+[s][\\.]$)"],
                    "preserve_original": True
                },
                "synonym" : {
                   "type" : "synonym",
                   "format": "wordnet",
                   "synonyms_path": "analysis/wn_s.pl"
               },
               "my_stemmer" : {
                    "type" : "stemmer",
                    "name" : "light_english"
                }
            },       
            "analyzer": {
                "english": {
                  "tokenizer": "standard",
                  "filter":  ["asciifolding", "lowercase", "english_stop",  
                            "english_keywords", "acronym_en_EN","synonym"]
                },
                "synonym" : {
                    "tokenizer" : "standard",
                    "filter" : ["english_stop", "asciifolding", "lowercase",
                                "english_keywords", "acronym_en_EN", "synonym","my_stemmer"]
            }
        }
    }
  }
}

r = requests.post("http://127.0.0.1:9200/relation" , data = json.dumps(query))
print r.content

