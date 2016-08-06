import urllib
from bs4 import BeautifulSoup
from urlparse import urlparse, parse_qs
import re

from elasticsearch import Elasticsearch,helpers


elasticsearch_ip = "127.0.0.1"+":9200"
es = Elasticsearch(hosts=[elasticsearch_ip])
bulk_limit = 10000

html = urllib.urlopen("http://dbpedia.org/sparql/?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fp+{%0D%0A++%3Fp+a+rdf%3AProperty+.%0D%0A++filter+contains%28str%28%3Fp%29%2C+%22%2Fontology%22%29+.%0D%0A}%0D%0A&format=text%2Fhtml&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=300000&debug=on")

soup = BeautifulSoup(html)

tr_list = soup.find_all("tr")
tr_list = tr_list[1:]

print len(tr_list)

tr_child_list = []
for x in xrange(0,len(tr_list)):
	for child in tr_list[x].children:
		if not child == "\n":
			tr_child_list.append(child)
	# print "*******"

print len(tr_child_list)


for x in xrange(0,len(tr_child_list)):
	for child in tr_child_list[x]:
		print child.contents

def camel_case_split(identifier):
    matches = re.finditer('(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', identifier)
    split_string = []
    # index of beginning of slice
    previous = 0
    for match in matches:
        # get slice
        split_string.append(identifier[previous:match.start()])
        # advance index
        previous = match.start()
    # get remaining string
    split_string.append(identifier[previous:])
    return " ".join(split_string)

ontology_list = []

for x in xrange(0,len(tr_child_list)):
	for child in tr_child_list[x]:
		temp = []
		temp.append(urlparse(child.contents[0]).path[10:])
		temp.append(camel_case_split(urlparse(child.contents[0]).path[10:]))
		ontology_list.append(temp)
		# ontology_list_split.append(camel_case_split(urlparse(child.contents[0]).path[10:]))
		# ontology_list.append(urlparse(child.contents[0]).path[10:])



actions = []
counter = 0
for pattern in ontology_list:
	action = {
		"_index" : "relation",
		"_type" : "patty_index",
		"_source" : {
			"relation" : str(pattern[0]),
			"pattern" : str(pattern[1])
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


