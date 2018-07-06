import argparse, os
import sqlalchemy
from tqdm import tqdm

from common.container.sparql import SPARQL
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.evaluation.oracle import Oracle
from common.utility.stats import Stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--database", help="input database", default="IQA.db", dest="database")
    parser.add_argument("--input", help="input file of Q/A dataset", default="data/LC-QuAD/linked.json", dest="input")
    args = parser.parse_args()

    dataset = LC_Qaud_Linked(os.path.join(args.base_path, 'data', 'LC-QuAD', 'linked.json'))
    parse_sparql = dataset.parser.parse_sparql
    engine = sqlalchemy.create_engine('sqlite:///{0}'.format(os.path.join(args.base_path, args.database)))

    oracle = Oracle()
    stats = Stats()

    # question_query = list(engine.execute(
    #     'select question_id, query from interaction_log where id in (select max(id) from interaction_log where username="fathoni" group by session_id)'))
    #
    # for item in question_query:
    #     results = list(engine.execute(
    #         'select question_id, final_query from answered_questions WHERE username = "fathoni" and question_id="{}"'.format(
    #             item[0])))
    #     if len(results) == 1:
    #         results = results[0]
    #         engine.execute(
    #             u'UPDATE answered_questions set final_query="{0}" WHERE username = "fathoni" and question_id="{1}"'.format(
    #                 item[1], item[0]))
    #     else:
    #         print 'error'

    username = 'fathoni'
    # username = 'debayan'
    answered_questions = list(engine.execute('SELECT * FROM answered_questions WHERE username = "{}"'.format(username)))
    print(len(answered_questions))
    for answered_question in answered_questions:
        qapair = dataset.get_by_id(answered_question[2])
        if len(qapair) > 0:
            qapair = qapair[0]
            query = answered_question[7]
            if query is None:
                stats.inc('NAN')
                continue
            if 'skip:' in query:
                stats.inc(query)
                result = False
            else:
                user_query = SPARQL(query, parse_sparql)
                result = oracle.validate_query(qapair, user_query)
                stats.inc('correct' if result else 'incorrect')
            print query
            print qapair.sparql.query
            print result

    print stats
