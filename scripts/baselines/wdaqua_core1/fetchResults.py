from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.parser.qald import Qald
from common.kb.dbpedia import DBpedia
from common.container.sparql import SPARQL
from common.utility.stats import Stats
from common.utility.utils import Utils
from tqdm import tqdm
import argparse
import os
import pickle as pk
import json


class FetchResults:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def fetch(self, question):
        data = {
            'query': question.encode('utf-8'),
            'kb': 'dbpedia',
            'lang': 'en'
        }
        return Utils.call_web_api(self.endpoint, data, use_json=False, use_url_encode=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset: lcquad, qald", default="lcquad", dest="dataset")
    parser.add_argument("--input", help="input file of Q/A dataset", default="data/LC-QuAD/linked.json", dest="input")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked2843_IOB.pk",
                        dest="gold_chunk")
    args = parser.parse_args()

    check_correct_quries = False
    fetch_results = False
    validate_results = True

    if args.dataset == 'lcquad':
        dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.input))
    elif args.dataset == 'qald':
        dataset = Qald(os.path.join(args.base_path, args.input))

    kb = DBpedia(endpoint='http://dbpedia.org/sparql', use_cache=False)
    parse_sparql = dataset.parser.parse_sparql

    if check_correct_quries:
        stats = Stats()
        correct_quries = []
        for qapair in tqdm(dataset.qapairs):
            result = kb.query(qapair.sparql.raw_query)
            try:
                if ('qa_results' in result[1] and len(result[1]['qa_results']['bindings']) > 0) or (
                        'boolean' in result[1] and result[1]['boolean']):
                    stats.inc('+correct')
                    correct_quries.append(qapair.id)
                else:
                    stats.inc('-incorrect')
            except:
                print("error")
                print(result)
                break
        print(stats)
        stats['correct_quries'] = correct_quries
        stats.save(os.path.join(args.base_path, 'output/correct_queries.json'))

    stats = Stats.load(os.path.join(args.base_path, 'output/correct_queries.json'))

    wdaqua_core1 = FetchResults(endpoint='http://wdaqua-core1.univ-st-etienne.fr/gerbil')

    qa_results = None
    if os.path.exists(os.path.join(args.base_path, 'output/wdaqua_core1.pk')):
        with open(os.path.join(args.base_path, 'output/wdaqua_core1.pk'), "rb") as data_file:
            qa_results = pk.load(data_file)

    if fetch_results:
        # qa_results = Stats.load(os.path.join(args.base_path, 'output/wdaqua_core1.json'))
        if qa_results is None:
            qa_results = Stats()
        for qapair in tqdm(dataset.qapairs):
            if qapair.id in stats['correct_quries'] and (
                    qapair.id not in qa_results or not isinstance(qa_results[qapair.id], dict)):
                try:
                    qa_results[qapair.id] = wdaqua_core1.fetch(qapair.question.text)
                    # qa_results.save(os.path.join(args.base_path, 'output/wdaqua_core1.json'))
                except Exception as expt:
                    qa_results[qapair.id] = expt
                with open(os.path.join(args.base_path, 'output/wdaqua_core1.pk'), "w") as data_file:
                    pk.dump(qa_results, data_file)

    fetch_gold_results = False
    if fetch_gold_results:
        qa_results = dict()
        if os.path.exists(os.path.join(args.base_path, 'output/gold_answer.pk')):
            with open(os.path.join(args.base_path, 'output/gold_answer.pk'), "r") as data_file:
                qa_results = pk.load(data_file)
        for qapair in tqdm(dataset.qapairs):
            if qapair.id in stats['correct_quries'] and (
                    qapair.id not in qa_results or not isinstance(qa_results[qapair.id], tuple)):
                try:
                    qa_results[qapair.id] = kb.query(qapair.sparql.raw_query)
                    # qa_results.save(os.path.join(args.base_path, 'output/wdaqua_core1.json'))
                except Exception as expt:
                    qa_results[qapair.id] = expt
                with open(os.path.join(args.base_path, 'output/gold_answer.pk'), "w") as data_file:
                    pk.dump(qa_results, data_file)

    validate_results = True
    if validate_results:
        if os.path.exists(os.path.join(args.base_path, 'output/gold_answer.pk')):
            with open(os.path.join(args.base_path, 'output/gold_answer.pk'), "rb") as data_file:
                ds_results = pk.load(data_file)

            final_stats = Stats()
            stats_results = Stats()
            for i in range(1, 10):
                stats_id = '#{}-'.format(i)
                stats_results[stats_id + 'p'] = []
                stats_results[stats_id + 'r'] = []
                stats_results[stats_id + 'f1'] = []
            for qapair in tqdm(dataset.qapairs):
                query_complexity = len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())])
                stats_id = '#{}-'.format(query_complexity)
                if qapair.id in qa_results:#qapair.id in stats['correct_quries']:
                    # try:
                    query_equal = qapair.sparql == SPARQL(
                        qa_results[qapair.id]['questions'][0]['question']['language'][0]['SPARQL'],
                        parse_sparql)
                    ds_answer = ds_results[qapair.id]
                    wdaqua_core1_answer = qa_results[qapair.id]
                    q1 = json.loads(wdaqua_core1_answer['questions'][0]['question']['answers'])
                    if ds_answer[1] is not None:
                        if 'boolean' in ds_answer[1]:
                            q2 = ds_answer[1]['boolean']
                        else:
                            q2 = ds_answer[1]['results']['bindings']
                            if 'callret-0' in q2[0]:
                                q2 = q2[0]['callret-0']['value']
                            else:
                                q2 = set([item['uri']['value'] for item in q2])

                        if 'boolean' in q1:
                            q1 = q1['boolean']
                            # if 'boolean' in q1 else bool(int(q1[0]['c']['value']))
                        else:
                            q1 = q1['results']['bindings']
                            if len(q1) > 0:
                                if 'c' in q1[0]:
                                    q1 = q1[0]['c']['value']
                                else:
                                    if 'o2' in q1[0]:
                                        id = 'o2'
                                    elif 'o1' in q1[0]:
                                        id = 'o1'
                                    elif 's0' in q1[0]:
                                        id = 's0'
                                    else:
                                        id = 's1'
                                    q1 = set([item[id]['value'] for item in q1])

                        p = 0
                        r = 0
                        f1 = 0
                        if q1 == q2:
                            p = r = f1 = 1
                            stats_results.inc('+correct')
                            final_stats[qapair.id] = '+correct'
                        elif isinstance(q1, set) and isinstance(q2, set):
                            tp = float(len(q2.intersection(q1)))
                            p = tp / len(q1)
                            r = tp / len(q2)
                            if (p + r) == 0:
                                f1 = 0
                            else:
                                f1 = 2 * ((p * r) / (p + r))
                            if tp > 0:
                                stats_results.inc('+partial')
                                final_stats[qapair.id] = '+partial'
                            else:
                                stats_results.inc('-incorrect')
                                final_stats[qapair.id] = '-incorrect'
                        else:
                            if query_equal:
                                print("qqq")
                            stats_results.inc('-incorrect')

                        stats_results[stats_id + 'p'].append(p)
                        stats_results[stats_id + 'r'].append(r)
                        stats_results[stats_id + 'f1'].append(f1)
                    else:
                        stats_results.inc('ds_answer_failed')

                    stats_results.inc('total')
                    stats_results.inc(stats_id + 'total')
                    # except Exception as expt:
                    #     print(expt)


            for i in range(1, 10):
                stats_id = '#{}-'.format(i)
                if stats_results[stats_id + 'total'] > 0:
                    p = sum(stats_results[stats_id + 'p']) / stats_results[stats_id + 'total']
                    r = sum(stats_results[stats_id + 'r']) / stats_results[stats_id + 'total']
                    f1 = sum(stats_results[stats_id + 'f1']) / stats_results[stats_id + 'total']
                    final_stats[i] = [p, r, f1, stats_results[stats_id + 'total']]
                    print(i, final_stats[i])

            final_stats.save(os.path.join(args.base_path, 'output/wd_perf.json'))
