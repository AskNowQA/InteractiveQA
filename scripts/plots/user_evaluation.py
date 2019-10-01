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
from common.kb.dbpedia import DBpedia

colors = {'NIB-IQA': 'white', 'IQA-IG': 'white', 'IQA-OG': 'white', 'SIB': 'white', 'NIB-WDAqua': 'white',
          'NIB-IQA-Top1': 'white'}

hatches = {'NIB-IQA': '', 'IQA-IG': '///', 'IQA-OG': '...', 'SIB': 'oo', 'NIB-WDAqua': '...',
           'NIB-IQA-Top1': ''}

linestyle = {'NIB-IQA': '-.', 'IQA-IG': ':', 'IQA-OG': '--', 'SIB': ':', 'NIB-WDAqua': '-',
             'NIB-IQA-Top1': '-'}
marker = {'NIB-IQA': 'v', 'IQA-IG': 'x', 'IQA-OG': 'o', 'SIB': '*', 'NIB-WDAqua': '+',
          'NIB-IQA-Top1': 'x'}
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
            'SELECT * FROM answered_questions WHERE username NOT IN ("tttt", "hamid123", "mohnishdresden")'))
    # WHERE username NOT IN ("Mohnish", "MouTn", "debayan", "nicolas", "shagha", "hamid", "afshin","thoms","sergej"
    count = 0
    correct_count = 0
    skip_count = 0
    for answered_question in answered_questions:
        qapair = dataset.get_by_id(answered_question[2])
        if len(qapair) > 0:
            qapair = qapair[0]
            query = answered_question[7]

            if query is None or 'skip:' in query:
                skip_count += 1
                continue
            else:
                user_query = SPARQL(query, parse_sparql)
                result = oracle.validate_query(qapair, user_query)
                if result:
                    correct_count += 1
                else:
                    count += 1
                    print(qapair.id)
                    print(query.encode("ascii", "ignore"))
                    print(qapair.sparql.query.encode("ascii", "ignore"))
                    print("")
                    print("")
    print(len(answered_questions), correct_count, skip_count, count)
    # 423 147
    # structure 55 0.37
    # type 39 0.26
    # completeness 6 0.04
    # benchmark 3 0.02
    # synonym 33 0.22
    # entity 6 0.04


def user_vs_benchmark(engine, dataset, username):
    query = """
    SELECT interaction_log.*, questions.complexity, assigned_questions.strategy  FROM interaction_log
    LEFT JOIN questions on questions.id=interaction_log.question_id
    INNER JOIN assigned_questions ON assigned_questions.question_id = interaction_log.question_id 
        AND assigned_questions.username = interaction_log.username
    WHERE 
      interaction_log.username NOT IN ('tttt', 'hamid123', 'mohnishdresden') AND 
      interaction_log.id IN (
        SELECT 
            MAX(interaction_log.id) as last_id
        FROM interaction_log
        WHERE interaction != "feedback"
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
        elif 'Is it what the question means?' in str(item['interaction']) and item[
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
        print(strategy)
        tmp = df.loc[df['strategy'] == strategy][
            ['complexity', 'u_correct', 'u_skip_question', 'u_skip_option', 'b_correct']].groupby(['complexity']).agg(
            ['count', 'sum'])
        tmp['u_correct_avg'] = tmp.u_correct['sum'] / tmp.u_correct['count'] * 100.0
        tmp['b_correct_avg'] = tmp.b_correct['sum'] / tmp.b_correct['count'] * 100.0
        tmp['u_skip_question_avg'] = tmp.u_skip_question['sum'] / tmp.u_skip_question['count'] * 100.0
        tmp['u_skip_option_avg'] = tmp.u_skip_option['sum'] / tmp.u_skip_option['count'] * 100.0
        print(tmp)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        x_range = np.array(range(2, 6))
        y_value = tmp['u_correct_avg']
        y_value_avg = "{:.1f}".format(sum(y_value) / len(y_value))
        ax.bar(x_range - .1, y_value, width=0.2, label='Conf-U [Avg: {}]'.format(y_value_avg)
               , edgecolor='black', hatch='...', color='white')
        for i, v in enumerate(y_value):
            ax.text(i + 1.8, v + .05, "{0:.0f}".format(v), color='black')
        y_value = tmp['b_correct_avg']
        y_value_avg = "{:.1f}".format(sum(y_value) / len(y_value))
        ax.bar(x_range + 0.1, y_value, width=0.2, label='Conf-B [Avg: {}]'.format(y_value_avg)
               , edgecolor='black', hatch='///', color='white')
        for i, v in enumerate(y_value):
            ax.text(i + 2, v + .05, "{0:.0f}".format(v), color='black')
        ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1, 1.02), borderaxespad=0.)
        plt.yticks(np.arange(0, 101, 10))
        plt.xticks(x_range)
        fig.tight_layout()
        plt.savefig('user_vs_benchmark-{}'.format(strategy))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_range = np.array(range(2, 6)) - 0.1
    for strategy in ['IG', 'OG']:
        print(strategy)
        tmp = df.loc[df['strategy'] == strategy][
            ['complexity', 'u_correct', 'u_skip_question', 'u_skip_option', 'b_correct']].groupby(['complexity']).agg(
            ['count', 'sum'])
        tmp['u_correct_avg'] = tmp.u_correct['sum'] / tmp.u_correct['count'] * 100.0
        tmp['b_correct_avg'] = tmp.b_correct['sum'] / tmp.b_correct['count'] * 100.0
        tmp['u_skip_question_avg'] = tmp.u_skip_question['sum'] / tmp.u_skip_question['count'] * 100.0
        tmp['u_skip_option_avg'] = tmp.u_skip_option['sum'] / tmp.u_skip_option['count'] * 100.0

        y_value = tmp['b_correct_avg']/100
        y_value_avg = "{:.2f}".format(sum(y_value) / len(y_value))
        ax.bar(x_range, y_value, width=0.2, label='F1-{} [Avg: {}]'.format(strategy, y_value_avg)
               , edgecolor='black', hatch=hatches['IQA-' + strategy], color='white')
        for i, v in enumerate(y_value):
            ax.text(x_range[i] - 0.2 + (0.1 if strategy == 'OG' else 0), v + .01, "{0:0.2f}".format(v), color='black')
        x_range += 0.2
    x_range = np.array(range(2, 6))
    ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1, 1.02), borderaxespad=0.)
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xticks(x_range)
    fig.tight_layout()
    plt.savefig('f1-IGOG')


def ig_vs_og(engine, strategy):
    query = """
        SELECT 
            questions.complexity,
            assigned_questions.strategy,
            questions.id,
            COUNT(interaction_log.id) AS num_inter
        FROM questions
            INNER JOIN assigned_questions ON assigned_questions.question_id = questions.id
            LEFT JOIN answered_questions ON answered_questions.question_id = assigned_questions.question_id 
                AND answered_questions.username = assigned_questions.username
            LEFT JOIN interaction_log ON interaction_log.question_id = assigned_questions.question_id 
                AND interaction_log.username = assigned_questions.username
        WHERE 
            interaction_log.username NOT IN ('tttt', 'hamid123', 'mohnishdresden') AND 
            assigned_questions.strategy IS NOT NULL
            AND interaction_log.interaction != "feedback"
        GROUP BY 
            assigned_questions.strategy, questions.complexity, questions.id"""
    #interaction_log.username NOT IN ("hamid123", "mohnishdresden", "sebastian", "ahcene") AND
    detailed_results = np.array(list(engine.execute(query)), dtype=object)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_range = np.array(range(2, 6))
    data = [(list(detailed_results[((detailed_results[:, 1] == strategy) & (detailed_results[:, 0] == x))][:, 3]))
            for x in x_range]
    bp = ax.boxplot(data, positions=x_range, showfliers=True)
    plt.xticks(x_range, x_range)
    plt.yticks(np.arange(1, 20, 2))
    # ax.legend([bp['boxes'][0]], [strategy], loc='lower right', ncol=2, bbox_to_anchor=(1, 1.02), borderaxespad=0.)
    fig.tight_layout()
    plt.savefig('{}.png'.format(strategy))
    print(strategy, np.mean([item for row in data for item in row]))
    print(data)


def feedback(engine, strategy='IG'):
    query = """
            SELECT 
                questions.complexity, 
                assigned_questions.strategy,
                questions.id,
                SUM(CAST(substr(interaction_log.data, 8,1) AS INTEGER)),
                SUM(CAST(substr(interaction_log.data, 17,1) AS INTEGER))
        FROM interaction_log
                INNER JOIN questions on questions.id == interaction_log.question_id
                INNER JOIN assigned_questions ON assigned_questions.question_id = interaction_log.question_id
                AND interaction_log.username = assigned_questions.username
            where
                interaction_log.username NOT IN ('tttt', 'hamid123', 'mohnishdresden') AND 
                interaction_log.interaction == 'feedback' 
                and interaction_log.data != '{"r1":"","r2":"","comment":""}'
            GROUP BY 
                questions.complexity, assigned_questions.strategy, questions.id"""
    detailed_results = np.array(list(engine.execute(query)), dtype=object)

    query = """
    SELECT 
		questions.complexity, 
		assigned_questions.strategy,
		SUM(CAST(substr(interaction_log.data, 8,1) AS INTEGER))*1.0/COUNT(interaction_log.id),
		SUM(CAST(substr(interaction_log.data, 17,1) AS INTEGER))*1.0/COUNT(interaction_log.id)
    FROM interaction_log
        INNER JOIN questions on questions.id == interaction_log.question_id
        INNER JOIN assigned_questions ON assigned_questions.question_id = interaction_log.question_id
        AND interaction_log.username = assigned_questions.username
    where
        interaction_log.username NOT IN ('tttt', 'hamid123', 'mohnishdresden') AND 
        interaction_log.interaction == 'feedback' 
        and interaction_log.data != '{"r1":"","r2":"","comment":""}'
    GROUP BY 
        questions.complexity, assigned_questions.strategy"""

    results = np.array(list(engine.execute(query)), dtype=object)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_range = np.array(range(2, 6))

    data = [(list(detailed_results[((detailed_results[:, 1] == strategy) & (detailed_results[:, 0] == x))][:, 3]))
            for x in x_range]
    bp = ax.boxplot(data, positions=x_range, showfliers=True)

    plt.xticks(x_range, x_range)
    plt.yticks(np.arange(1, 6, 1))
    # ax.legend(loc='lower right', ncol=2, bbox_to_anchor=(1, 1.02), borderaxespad=0.)
    fig.tight_layout()
    plt.savefig('feedback-{}.png'.format(strategy))

    print(np.mean([x for row in data for x in row]))
    print(results)


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

    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    oracle = Oracle(kb)
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
    ig_vs_og(engine, 'IG')
    ig_vs_og(engine, 'OG')
    # feedback(engine, 'IG')
    # feedback(engine, 'OG')
