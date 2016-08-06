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

#for parsing wikipedia-patterns.txt
file = open("patty-dataset/wikipedia-patterns.txt")	#open File
reader = csv.reader(file, delimiter = '\t')
wikipedia_patterns = []
counter = 0
for row in reader:
	temp = row[1].split("$")			#splitting
	temp = temp[:-1]					#last elemnt in the list is empty
	#for removng semicolon from the list end
	for position in xrange(len(temp)):
		temp[position] = temp[position][:-1]
	row[1] = temp
	wikipedia_patterns.append(row)
file.close()

print "done parsing wikipedia_patterns text file"


#parsing wikipedia-subsumptions.txt
file = open("patty-dataset/wikipedia-subsumptions.txt")	#open File
counter = 0
reader = csv.reader(file, delimiter = '\t')
subsumption_list = {}


for row in reader:
	value = []
	value.append(row[1])
	value.append(row[2])
	if row[0] in subsumption_list:
		temp = subsumption_list[row[0]]
		temp.append(value)
		subsumption_list[row[0]] = temp
	else:
		temp = []
		temp.append(value)
		subsumption_list[row[0]] = temp

file.close()

print "donoe parsing wikipedia-subsumptions text file"

#indexing dbpedia-relation-phrases text file
actions = []
counter = 0
for pattern in pattern_list:
	action = {
		"_index" : "patty-dataset",
		"_type" : "dbpedia-relation-paraphrases",
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



#indexing wikipedia-patterns text file
actions = []
counter = 0
for pattern in wikipedia_patterns:
	try:
		action = {
			"_index" : "patty-dataset",
			"_type" : "wikipedia-patterns",
			"_source" : {
			#patternid	patterntext	confidence	domain	range
				"patternid" : pattern[0],
				"patterntext" : pattern[1],
				"confidence" : pattern[2],
				"domain" : pattern[3],
				"range" : pattern[4]
			}
		}
		actions.append(action)
		counter = counter + 1
		if counter > bulk_limit:
			counter = 0
			helpers.bulk(es, actions)
			actions = []
	except:
		continue						
helpers.bulk(es, actions)


print "done indexing wikipedia-patterns"

#indexing wikipedia-subsumptions text file
actions = []
counter = 0
for pattern in subsumption_list:
	action = {
		"_index" : "patty-dataset",
		"_type" : "wikipedia-subsumptions",
		"_source" : {
			"patternid" : pattern,
			"subsumption_list" : subsumption_list[pattern]
		}
	}
	actions.append(action)
	counter = counter + 1
	if counter > bulk_limit:
		counter = 0
		helpers.bulk(es, actions)
		actions = []		
helpers.bulk(es, actions)

print "done indexing wikipedia-subsumptions"
print "Hello world .. All subsumptions patterns are under control"
