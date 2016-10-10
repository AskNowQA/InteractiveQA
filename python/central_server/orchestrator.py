from bottle import route, run, get, post, request, response
from pprint import pprint
import json
import requests


question_url = "http://0.0.0.0:4568/question"
entitySpotting_url = "http://0.0.0.0:4568/entity_spotting"
@post('/question')
def central_server():
	#rest api post call question:
	question = request.forms.get('question')
	#send the question to java
	payload = {"question":question}
	question_nqs = requests.post(question_url,data=payload)
	payload = {"question":question, "nqs":question_nqs}
	nqs_entitySpotting = requests.post(entitySpotting_url,data=payload)
	return nqs_entitySpotting

run(host='localhost', port=8080, debug=True)