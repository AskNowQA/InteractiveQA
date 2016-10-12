from bottle import route, run, template, static_file, request,get,post, response,jinja2_template as template
from pprint import pprint
import json
import requests
import ast
#Macros
entitySpotting_url = "http://0.0.0.0:4568/entity_spotting"
question_url = "http://0.0.0.0:4568/question"
#rendering static files
#TODO- add more static files.
@route('/images/<filename:path>')
def send_static(filename):
    print filename, "images"
    return static_file(filename, root='images/')

@route('/js/typed/<filename:path>')
def send_static(filename):
    print filename, "images"
    return static_file(filename, root='js/typed/')

@route('/fonts/<filename:path>')
def send_static(filename):
    print filename, "images"
    return static_file(filename, root='fonts/')

#testing
@route('/helloworld')
def test_helloWorld():
	print "I am there !"
	return template("landingpage3.html")

@get("/")
def landingpage():
	print "@landingpage"
	return template("landingpage3.html")

@get("/question")
def question_page_render():
	print "@question page render"
	return template("landingpage3.html")

@post("/question")
def question():
	print "@question"
	question = {}
	#receive question from the user
	data = request.json
	question["text"] = data["question"]
	print question["text"]
	#send the question to java
	payload = {"question":question["text"]}
	question["nqs"] = requests.post(question_url,data=payload).content	#stores the nqs of the question
	#for entity spotting
	print question["nqs"]
	payload = {"question":question["text"], "nqs":question["nqs"]}
	nqs_entitySpotting = requests.post(entitySpotting_url,data=payload).content
	nqs_entitySpotting = json.loads(nqs_entitySpotting)
	pprint(nqs_entitySpotting)
	#convert string to list
	# nqs_entitySpotting = nqs_entitySpotting[1:-1]
	# nqs_entitySpotting = nqs_entitySpotting.split(",")
	question["entity"] = nqs_entitySpotting
	return json.dumps(question)


if __name__ == "__main__":
	run(host='0.0.0.0', port=9000, debug=False,server = 'gunicorn',workers = 1)