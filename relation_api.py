#this starts the server which accepts external requets 
#its a simple bottle server listening at localhost:8081
#to send request at this server r = requests.post("http://127.0.0.1:8081/relation",data={"keyword":"song"})


from bottle import route, run, template, request
import requests,json


@route('/relation',method="post")
def relation():
	keyword = request.forms.get("keyword")
	#form a query	
	query = {
    "query": {
        "bool": {
            "must": [
               {
                   "match": {
                      "pattern": keyword
                   }
               }
            ]
        }
    }
}
	#sending request to elasticsearch
	r = requests.post('http://127.0.0.1:9200/relation/patty_index/_search', data = json.dumps(query))
	#parsing the elasticsearch output
	content = json.loads(r.content)
	content = content["hits"]["hits"]
	for element in content:
		element.pop("_id")
		element.pop("_type")
		element.pop("_index")
	#done parsng and sending back the output of elasticsearch
	return json.dumps(content)	
run(host='0.0.0.0', port=8081)
