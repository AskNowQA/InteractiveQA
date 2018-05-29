from flask import Flask, render_template, request
from flask import jsonify
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "dfdfdffdad"

@app.route('/mystringa')
def mystringa():
    #if not flask.request.json:
     #   flask.abort(400)

    #userid = flask.request.json['userid']

    result = {'question': 'Name the municipality of Robert Clemente Bridge?',
              'IO': {'surface': 'Robert Clemente Bridge',
                     'values': ['Robert Clemente Bridge', 'Robert Clemente Community School']}}

    #data = json.dumps(result)
    #return json.dumps(result)
    return jsonify(result)


@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug = True)
