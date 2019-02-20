#!flask/bin/python

import os
import argparse
import logging
import flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from common.kb.dbpedia import DBpedia
from common.utility.utils import Utils
from common.utility.cacheDict import CacheDict
from common.utility.reverseProxied import ReverseProxied
from UI.database.tabledef import User
from UI.views.generalView import GeneralView
from UI.views.surveyView import SurveyView
from UI.views.freeQuestionSurveyView import FreeQuestionSurveyView
from UI.views.demoView import DemoView

app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/IQA.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'GeneralView:login'

global LoginForm
global kb

GeneralView.db = db
SurveyView.db = db
FreeQuestionSurveyView.db = db
DemoView.db = db

GeneralView.register(app)
SurveyView.register(app)
FreeQuestionSurveyView.register(app)
DemoView.register(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


if __name__ == '__main__':
    global kb
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--port", help="port", default=5001, type=int, dest="port")
    parser.add_argument("--base_path", help="base path", default="../", dest="base_path")
    args = parser.parse_args()
    logger.info(args)

    cache_path = os.path.join(args.base_path, "caches/")
    kb = DBpedia(cache_path=cache_path, use_cache=True)
    SurveyView.kb = kb
    FreeQuestionSurveyView.kb = kb
    DemoView.kb = kb

    Utils.set_cache_path(cache_path)
    app.run(debug=True, host='0.0.0.0', port=args.port)
