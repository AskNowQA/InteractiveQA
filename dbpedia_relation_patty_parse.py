#this files parese the patty's dbpedia-relation-paraphrases.txt file and indexes it in elasticsearch
import csv
from elasticsearch import Elasticsearch,helpers


elasticsearch_ip = "127.0.0.1"+":9200"
es = Elasticsearch(hosts=[elasticsearch_ip])
bulk_limit = 10000

#parsing dbpedia-relation-paraphrases.txt
file = open("patty-dataset/dbpedia-relation-paraphrases.txt")	#open File
reader = csv.reader(file, delimiter = '\t')
pattern_list = []
for row in reader:
	row[1] = row[1][:-1]		#to remove semicolon from the end of data
	pattern_list.append(row)
file.close()


print "done parsing dbpedia-relation-paraphrases text file"

#bulk-update in elasticsearch
actions = []
counter = 0
for pattern in pattern_list:
	action = {
		"_index" : "relation",
		"_type" : "patty_index",
		"_source" : {
			"relation" : pattern[0],
			"pattern" : pattern[1]
		}
	}
	actions.append(action)
	counter = counter + 1
	if counter > bulk_limit:
		counter = 0
		helpers.bulk(es, actions)
		actions = []		

helpers.bulk(es, actions)

print "done indexing dbpedia-relation-paraphrases"


