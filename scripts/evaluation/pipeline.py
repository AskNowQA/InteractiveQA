from common.pipeline import IQAPipeline
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.parser.qald import Qald
from common.interaction.interactionOptions import InteractionOptions
from common.evaluation.oracle import Oracle
from common.kb.dbpedia import DBpedia
from common.utility.stats import Stats
from common.container.sparql import SPARQL
from common.component.linker.goldLinker import GoldLinker
from scripts.evaluation.linker import LinkerEvaluator
from tqdm import tqdm
import argparse
import os
import pickle as pk
import re

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset: lcquad, qald", default="lcquad", dest="dataset")
    parser.add_argument("--input", help="input file of Q/A dataset", default="data/LC-QuAD/linked.json", dest="input")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked2843_IOB.pk",
                        dest="gold_chunk")
    parser.add_argument("--chunkers", help="[mdp, gold, senna, nltk]", default="mdp", dest="chunkers")
    parser.add_argument("--linkers", help="[mdp, falcon, earl]", default="mdp", dest="linkers")
    args = parser.parse_args()

    dataset = [{"question": "Name the municipality of Roberto Clemente Bridge ?"}]
    if args.dataset == 'lcquad':
        dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.input))
    elif args.dataset == 'qald':
        dataset = Qald(os.path.join(args.base_path, args.input))

    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    parse_sparql = dataset.parser.parse_sparql
    pipeline = IQAPipeline(args, kb, parse_sparql)
    oracle = Oracle(kb)
    linker_evaluator = LinkerEvaluator(GoldLinker())

    pipeline_path = os.path.join(args.base_path, 'output', 'pipeline')
    if not os.path.exists(pipeline_path):
        os.mkdir(pipeline_path)

    interaction_types = [[False, True], [True, True]]
    strategies = ['InformationGain', 'OptionGain']  # , 'Probability']
    w = 1

    stats = {('IQA-AO' if all(type) else 'IQA-SO') + '-' + strategy: Stats() for strategy in strategies for type
             in interaction_types}
    stats['general'] = Stats()
    stats['general']['matched'] = []
    stats['general']['-ent_rel'] = []
    stats['general']['-ent'] = []
    stats['general']['-rel'] = []
    stats['general']['-no_query'] = []
    stats['general']['-extra-ent'] = []
    stats['general']['-extra-rel'] = []
    stats['general']['+correct_ids'] = []
    stats['general']['-no-ent'] = []
    stats['general']['-no-rel'] = []

    # baseline
    stats['IQA-SO-RQ'] = Stats()

    with open(os.path.join(args.base_path, 'output', 'wdaqua_core1.pk'), 'rb') as data_file:
        wdaqua_results = pk.load(data_file)

    question_complexities = {
        qapair.id: len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())]) for
        qapair in dataset.qapairs if qapair.id in wdaqua_results}

    qid = ''

    for qapair in tqdm(dataset.qapairs):
        if qapair.id not in wdaqua_results:
            continue
        qid = qapair.id
        stats['general'].inc("total")

        output_path = os.path.join(pipeline_path, ('{0}.pickle'.format(qapair.id)))
        if not os.path.exists(output_path):
            if True:
                try:
                    question = qapair.question.text
                    question = re.sub(r'[^\w+]', ' ', qapair.question.text).replace('TV', 'television').replace(' tv ',
                                                                                                                ' television ')
                    del pipeline.pipelines[0][0].cache[question]
                except:
                    pass

            outputs, done, num_pipelines = pipeline.run(qapair)
            if len(outputs.queue) > 0:
                outputs = list(outputs.queue)
            else:
                outputs = [[], [], [], [], []]
            # save the output of the pipeline
            with open(output_path, 'wb') as file_handler:
                pk.dump(outputs, file_handler)
        else:
            with open(output_path, 'rb') as file_handler:
                outputs = pk.load(file_handler)

        analyze_failure = False
        for interaction_type in interaction_types:
            interaction_type_str = 'IQA-AO' if all(interaction_type) else 'IQA-SO'

            # baseline: ranked queries
            if interaction_type_str == 'IQA-SO':
                interaction_options = InteractionOptions(outputs, kb.parse_uri, parse_sparql, kb,
                                                         *interaction_type)
                ranked_queries = interaction_options.ranked_queries()
                stats[interaction_type_str + '-RQ'].inc(qid, 0)
                found = False
                for query in ranked_queries:
                    if oracle.validate_query(qapair, SPARQL(query['query'], parse_sparql)):
                        found = True
                        break
                    stats['IQA-SO-RQ'].inc(qid)
                if found:
                    stats['IQA-SO-RQ'].inc(qid + "+correct")
                    stats['general']['+correct_ids'].append(qid)
                else:
                    # if not found:
                    #     outputs, done, num_pipelines = pipeline.run(qapair)
                    # if question_complexities[qid] == 4:
                    print()
                    print(qapair.question.text)
                    print(qapair.sparql.raw_query)
                    stats['IQA-SO-RQ'].inc(qid + "-incorrect")
                    analyze_failure = True

            for strategy in strategies:
                found = False
                stats[interaction_type_str + '-' + strategy].inc(qid, 0)
                interaction_options = InteractionOptions(outputs, kb.parse_uri, parse_sparql, kb,
                                                         *interaction_type)
                while interaction_options.has_interaction():
                    if oracle.validate_query(qapair, interaction_options.query_with_max_probability()):
                        found = True
                        break

                    if strategy == 'InformationGain':
                        io = interaction_options.interaction_with_max_information_gain()
                    elif strategy == 'OptionGain':
                        io = interaction_options.interaction_with_max_option_gain(w)
                    elif strategy == 'Probability':
                        io = interaction_options.interaction_with_max_probability()

                    interaction_options.update(io, oracle.answer(qapair, io))
                    stats[interaction_type_str + '-' + strategy].inc(qid)

                if found or oracle.validate_query(qapair, interaction_options.query_with_max_probability()):
                    stats[interaction_type_str + '-' + strategy].inc(qid + "+correct")
                else:
                    stats[interaction_type_str + '-' + strategy].inc(qid + "-incorrect")
                    # analyze_failure = True

        if analyze_failure:
            stats['general'].inc('-incorrect')

            if len(outputs[0]) > 0:
                try:
                    item = outputs[0][1][0]

                    no_entity = len(item['entities']) == 0
                    no_relation = len(item['relations']) == 0
                    extra_entity = len(item['entities']) > len(
                        [uri_o for uri_o in qapair.sparql.uris if uri_o.is_entity()])
                    extra_relation = len(item['relations']) > len(
                        [uri_o for uri_o in qapair.sparql.uris if uri_o.is_ontology()])
                    wrong_entity = [uri_o for uri_o in qapair.sparql.uris if uri_o.is_entity() and uri_o.uri not in set(
                        [uri['uri'] for item in outputs[0][1] for ents in item['entities'] for uri in ents['uris'] if
                         len(item['entities']) > 0])]
                    wrong_relation = [uri_o for uri_o in qapair.sparql.uris if
                                      uri_o.is_ontology() and uri_o.uri not in set(
                                          [uri['uri'] for item in outputs[0][1] for ents in item['relations'] for uri in
                                           ents['uris'] if
                                           len(item['relations']) > 0])]
                    info = [qid, qapair.question.text, len([uri for uri in qapair.sparql.uris if not uri.is_generic()]),
                            len([uris.uri for uris in qapair.sparql.uris if not uris.is_generic()]) > len(
                                set([uris.uri for uris in qapair.sparql.uris if not uris.is_generic()])),
                            [item.uri for item in wrong_entity],
                            [item.uri for item in wrong_relation]]
                    matched = True
                    ent_rel = False
                    if not (no_entity or no_relation) and len(wrong_entity) > 0 and len(wrong_relation) > 0:
                        stats['general']['-ent_rel'].append(info)
                        matched = False
                        ent_rel = True
                    if no_entity:
                        stats['general']['-no-ent'].append(info)
                        matched = False
                    elif not ent_rel and len(wrong_entity) > 0:
                        stats['general']['-ent'].append(info)
                        matched = False
                    if no_relation:
                        stats['general']['-no-rel'].append(info)
                        matched = False
                    elif not ent_rel and len(wrong_relation) > 0:
                        stats['general']['-rel'].append(info)
                        matched = False
                    if extra_entity:
                        stats['general']['-extra-ent'].append(info)
                        matched = False
                    if extra_relation:
                        stats['general']['-extra-rel'].append(info)
                        matched = False

                    if matched:
                        stats['general']['matched'].append(info)
                except:
                    pass
            else:
                stats['general']['-no_query'].append([qid, qapair.question.text])
        else:
            stats['general'].inc('+correct')
            # stats['general']['corrects'].append(qid)
        for k, v in stats.items():
            v.save(os.path.join(args.base_path, 'output', 'stats-{0}.json'.format(k)))

    print(stats)
