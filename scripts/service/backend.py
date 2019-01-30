import sys
import os

module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import flask
import argparse
import logging
from common.utility.utils import Utils
from common.kb.dbpedia import DBpedia
from common.parser.lc_quad_linked import LC_Qaud_Linked

from common.interaction.bookKeeper import BookKeeper
from UI.backend.models.survey import Survey
from UI.backend.models.freeQuestionSurvey import FreeQuestionSurvey

app = flask.Flask(__name__)
app.secret_key = 'sec key'

Survey.register(app)
FreeQuestionSurvey.register(app)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    Utils.setup_logging()
    parser = argparse.ArgumentParser(description='UI Backend')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument("--port", help="port", default=5002, type=int, dest="port")
    args = parser.parse_args()
    logger.info(args)

    pipeline_path = os.path.join(args.base_path, 'output', 'pipeline')
    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    dataset = LC_Qaud_Linked(os.path.join(args.base_path, 'data', 'LC-QuAD', 'linked.json'))
    interaction_types = [[False, True], [True, True]]
    strategy = 'InformationGain'
    book_keeper = BookKeeper(os.path.join(args.base_path, 'UI', 'database', 'IQA.db'))

    Survey.dataset = dataset
    Survey.kb = kb
    Survey.strategy = strategy
    Survey.pipeline_path = pipeline_path
    Survey.book_keeper = book_keeper

    FreeQuestionSurvey.parser = dataset.parser
    FreeQuestionSurvey.strategy = strategy
    FreeQuestionSurvey.kb = kb
    FreeQuestionSurvey.args = args
    FreeQuestionSurvey.book_keeper = book_keeper

    app.run(debug=False, port=args.port)
