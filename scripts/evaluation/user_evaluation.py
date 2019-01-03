import argparse, os
import sqlalchemy
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import pandas as pd

from common.container.sparql import SPARQL
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.evaluation.oracle import Oracle
from common.utility.stats import Stats

colors = {'NIB-IQA': 'green', 'IQA-IG': 'blue', 'IQA-OG': 'orange', 'SIB': 'red', 'NIB-WDAqua': 'yellow',
          'NIB-IQA-Top1': 'blue'}
font = {'size': 14}
matplotlib.rc('font', **font)


def validate_query(dataset, qid, query):
    qapair = dataset.get_by_id(qid)
    if len(qapair) > 0:
        qapair = qapair[0]
        if query is None:
            return None
        if 'skip:' in query:
            return query
        else:
            user_query = SPARQL(query, parse_sparql)
            result = oracle.validate_query(qapair, user_query)
            return result
    return None


def error_analysis(engine, dataset):
    answered_questions = list(
        engine.execute(
            'SELECT * FROM answered_questions WHERE username NOT IN ("Mohnish", "MouTn", "debayan", "nicolas", "shagha", "hamid", "afshin","thoms","sergej")'))

    count = 0
    for answered_question in answered_questions:
        qapair = dataset.get_by_id(answered_question[2])
        if len(qapair) > 0:
            qapair = qapair[0]
            query = answered_question[7]

            if query is None or 'skip:' in query:
                continue
            else:
                user_query = SPARQL(query, parse_sparql)
                result = oracle.validate_query(qapair, user_query)
                if not result:
                    count += 1
                    print qapair.id
                    print query.encode("ascii", "ignore")
                    print qapair.sparql.query.encode("ascii", "ignore")
                    print ("")
                    print ("")
    print(len(answered_questions)), count
    # 423 147
    # structure 55 0.37
    # type 39 0.26
    # completeness 6 0.04
    # benchmark 3 0.02
    # synonym 33 0.22
    # entity 6 0.04


def user_vs_benchmark(engine, dataset, username):
    query = """
    SELECT 
        interaction_log.username,
        interaction_log.question_id,
        COUNT(DISTINCT interaction_log.session_id) AS session_count,
        MAX(interaction_log.id) AS max_id
    FROM interaction_log
    GROUP BY
        interaction_log.username,
        interaction_log.question_id
    HAVING
        COUNT(DISTINCT interaction_log.session_id) > 1"""
    interactions_multiple_session = pd.read_sql(query, engine)

    query = """
    SELECT interaction_log.*, questions.complexity, assigned_questions.strategy  FROM interaction_log
    LEFT JOIN questions on questions.id=interaction_log.question_id
    INNER JOIN assigned_questions ON assigned_questions.question_id = interaction_log.question_id 
        AND assigned_questions.username = interaction_log.username
    WHERE interaction_log.username NOT IN ("Mohnish", "MouTn", "debayan", "nicolas", "shagha", "hamid", "afshin","thoms","sergej") 
      AND interaction_log.id IN (
        SELECT 
            MAX(interaction_log.id) as last_id
        FROM interaction_log
        GROUP BY
            interaction_log.question_id,
            interaction_log.session_id)"""
    interactions = pd.read_sql(query, engine)

    df = pd.DataFrame(
        columns=['username', 'complexity', 'strategy', 'question_id', 'u_correct', 'u_skip_question', 'u_skip_option',
                 'b_correct'])
    for row in interactions.iterrows():
        item = row[1]

        u_correct = 0
        u_skip_question = 0
        u_skip_option = 0
        b_correct = 0
        if item['data'] == 'early_correct':
            u_correct = 1
        elif 'skip:question_not_understandable' in item['data']:
            u_skip_question = 1
        elif 'skip:IO_not_understandable' in item['data']:
            u_skip_option = 1
        elif 'Is it what the question means?' in item['interaction'] and item[
            'answer'] == 'True':
            u_correct = 1
        elif item['data'] == '' and item['answer'] == '':
            continue

        b_correct = 1 if validate_query(dataset, item['question_id'], item['query']) == True else 0
        df.loc[len(df)] = [item['username'], item['complexity'], item['strategy'], item['question_id'], u_correct,
                           u_skip_question,
                           u_skip_option,
                           b_correct]
    for strategy in ['IG', 'OG']:
        print strategy
        tmp = df.loc[df['strategy'] == strategy][
            ['complexity', 'u_correct', 'u_skip_question', 'u_skip_option', 'b_correct']].groupby(['complexity']).agg(
            ['count', 'sum'])
        tmp['u_correct_avg'] = tmp.u_correct['sum'] / tmp.u_correct['count'] * 100.0
        tmp['b_correct_avg'] = tmp.b_correct['sum'] / tmp.b_correct['count'] * 100.0
        tmp['u_skip_question_avg'] = tmp.u_skip_question['sum'] / tmp.u_skip_question['count'] * 100.0
        tmp['u_skip_option_avg'] = tmp.u_skip_option['sum'] / tmp.u_skip_option['count'] * 100.0
        print tmp

        fig = plt.figure()
        ax = fig.add_subplot(111)
        x_range = np.array(range(2, 6))
        ax.bar(x_range - .1, tmp['u_correct_avg'], width=0.2, label='Conf-U')
        for i, v in enumerate(tmp['u_correct_avg']):
            ax.text(i + 1.8, v + .05, "{0:.0f}".format(v), color='black')
        ax.bar(x_range + 0.1, tmp['b_correct_avg'], width=0.2, label='Conf-B')
        for i, v in enumerate(tmp['b_correct_avg']):
            ax.text(i + 2, v + .05, "{0:.0f}".format(v), color='black')
        ax.legend(loc='upper right')
        plt.yticks(np.arange(0, 101, 10))
        plt.xticks(x_range)
        plt.savefig('user_vs_benchmark-{}'.format(strategy))


def ig_vs_og(engine):
    query = """
    SELECT 
        questions.complexity,
        assigned_questions.strategy,
        COUNT(DISTINCT assigned_questions.id) AS question_counts,
        COUNT(DISTINCT answered_questions.id) AS answered_question_counts,
        COUNT(interaction_log.id) AS num_inter
    FROM questions
        INNER JOIN assigned_questions ON assigned_questions.question_id = questions.id
        LEFT JOIN answered_questions ON answered_questions.question_id = assigned_questions.question_id 
            AND answered_questions.username = assigned_questions.username
        LEFT JOIN interaction_log ON interaction_log.question_id = assigned_questions.question_id 
            AND interaction_log.username = assigned_questions.username
    WHERE 
        assigned_questions.strategy IS NOT NULL
        AND interaction_log.username NOT IN ("elena", "elena2","Mohnish","Dubey", "hamid1")
    GROUP BY 
        assigned_questions.strategy, questions.complexity"""

    results = np.array(list(engine.execute(query)), dtype=object)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    y_value = 1.0 * results[:4][:, 4] / results[:4][:, 3]
    x_range = np.array(results[:4][:, 0], dtype=int)
    ax.bar(x_range - 0.1, y_value, color=colors['IQA-IG'], label='IQA-IG',
           width=0.2)
    for i, v in enumerate(y_value):
        ax.text(i + 1.8, v + .05, "{0:.1f}".format(v), color='black')

    y_value = 1.0 * results[4:][:, 4] / results[4:][:, 3]
    ax.bar(x_range + 0.1, 1.0 * results[4:][:, 4] / results[4:][:, 3], color=colors['IQA-OG'], label='IQA-OG',
           width=0.2)
    for i, v in enumerate(y_value):
        ax.text(i + 2, v + .05, "{0:.1f}".format(v), color='black')

    plt.xticks(x_range, x_range)
    ax.legend(loc='upper center', ncol=2, bbox_to_anchor=(0.742, 1.06))
    fig.tight_layout()
    plt.savefig('ig_vs_og.png')

    print results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--database", help="input database", default="UI/database/IQA.db", dest="database")
    parser.add_argument("--input", help="input file of Q/A dataset", default="data/LC-QuAD/linked.json", dest="input")
    parser.add_argument("--username", help="username", default="hamid", dest="username")
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

    # error_analysis(engine, dataset)
    # user_vs_benchmark(engine, dataset, args.username)
    ig_vs_og(engine)
