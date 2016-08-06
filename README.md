Steps to run the code 

1> kill the elasticsearch server process
2> Copy the analysis folder from extra and paste it in config folder in elasticsearch directory 
3> Install all the modules given below. There might be some more modules which I forgot to specify 

	requests
	json
	elasticsearch
	bottle
	beautifulsoup
	urllib

4>start the elasticsearch process .. This can be done by going into bin folder in elasticsearch directory and then issue command ./elasticsearch

4b> Downlaod the patty dataset from this link - http://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/patty/
Scroll down in the link and you will find download link - Dataset (Wordnet types): pattern synsets, subsumptions and instances

Make sure you have downloaded in the same directory as these other files (elasticsearch_index.py; dbpedia_relation_patty_parse)

5>Run the file elasticsearch_index.py  .. python elasticsearch_index.py
6> Similarly run dbpedia_relation_patty_parse and then parsing_ontology.py

7>Finally after these run relation_api.py

At this point one will have a server which accepts a post request at port number 8081 and accepts a single phrase to check for relation with parameter being "keyword" and url being localhost/relation . 

For example 
1>open python in terminal and then issue following commands 
import requests

r = requests.post("http://127.0.0.1:8081/relation",data=json.dumps({"keyword":"song"})) 
#please note that song here can be replaced by some other relation phrase

print r.content



##to-do 
1>Write a script to automate these tasks 
2>Add comments to the code 	