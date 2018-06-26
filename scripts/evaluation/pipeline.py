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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset: lcquad, qald", default="lcquad", dest="dataset")
    parser.add_argument("--input", help="input file of Q/A dataset", default="data/LC-QuAD/linked.json", dest="input")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked2843_IOB.pk",
                        dest="gold_chunk")
    args = parser.parse_args()

    dataset = [{"question": "Name the municipality of Roberto Clemente Bridge ?"}]
    if args.dataset == 'lcquad':
        dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.input))
    elif args.dataset == 'qald':
        dataset = Qald(os.path.join(args.base_path, args.input))

    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    parse_sparql = dataset.parser.parse_sparql
    pipeline = IQAPipeline(args, kb, parse_sparql)
    oracle = Oracle()
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

    # baseline
    stats['IQA-SO-RQ'] = Stats()

    with open(os.path.join(args.base_path, 'output', 'wdaqua_core1.pk'), "r") as data_file:
        wdaqua_results = pk.load(data_file)

    qid = -1
    for qapair in tqdm(dataset.qapairs):
        qid += 1
        stats['general'].inc("total")
        # if stats['general']['total'] - 1 not in [10, 19, 20, 37, 40, 50, 52]:
        #     continue
        # if 'zoro' in qapair.question.text.lower():
        #     continue
        # if stats['general']['total'] > 100:
        #     break
        if qapair.id not in wdaqua_results:
            continue

        output_path = os.path.join(pipeline_path, ('{0}.pickle'.format(qapair.id)))
        if not os.path.exists(output_path):
            outputs = pipeline.run(qapair)
            # save the output of the pipeline
            with open(os.path.join(pipeline_path, ('{0}.pickle'.format(qapair.id))), 'w') as file_handler:
                pk.dump(outputs, file_handler)
        else:
            with open(os.path.join(pipeline_path, ('{0}.pickle'.format(qapair.id))), 'r') as file_handler:
                outputs = pk.load(file_handler)

        analyze_failure = False
        for interaction_type in interaction_types:
            interaction_type_str = 'IQA-AO' if all(interaction_type) else 'IQA-SO'

            # baseline: ranked queries
            if interaction_type_str == 'IQA-SO':
                interaction_options = InteractionOptions(outputs[2], kb.parse_uri, parse_sparql, kb, *interaction_type)
                ranked_queries = interaction_options.ranked_queries()
                stats[interaction_type_str + '-RQ'].inc(str(qid), 0)
                found = False
                for query in ranked_queries:
                    if oracle.validate_query(qapair, SPARQL(query['query'], parse_sparql)):
                        found = True
                        break
                    stats['IQA-SO-RQ'].inc(str(qid))
                if found:
                    stats['IQA-SO-RQ'].inc(str(qid) + "+correct")
                else:
                    stats['IQA-SO-RQ'].inc(str(qid) + "-incorrect")
                    analyze_failure = True

            for strategy in strategies:
                found = False
                stats[interaction_type_str + '-' + strategy].inc(str(qid), 0)
                interaction_options = InteractionOptions(outputs[2], kb.parse_uri, parse_sparql, kb, *interaction_type)
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
                    stats[interaction_type_str + '-' + strategy].inc(str(qid))

                if found or oracle.validate_query(qapair, interaction_options.query_with_max_probability()):
                    stats[interaction_type_str + '-' + strategy].inc(str(qid) + "+correct")
                else:
                    stats[interaction_type_str + '-' + strategy].inc(str(qid) + "-incorrect")
                    # analyze_failure = True

        if analyze_failure:
            item = outputs[1][-1]
            stats['general'].inc('-incorrect')

            wrong_entity = [uri_o for uri_o in qapair.sparql.uris if uri_o.is_entity() and uri_o.uri not in set(
                [uri['uri'] for item in outputs[1] for ents in item['entities'] for uri in ents['uris'] if
                 len(item['entities']) > 0])]
            wrong_relation = [uri_o for uri_o in qapair.sparql.uris if uri_o.is_ontology() and uri_o.uri not in set(
                [uri['uri'] for item in outputs[1] for ents in item['relations'] for uri in ents['uris'] if
                 len(item['relations']) > 0])]
            info = [qid, qapair.question.text, len([uri for uri in qapair.sparql.uris if not uri.is_generic()]),
                    len([uris.uri for uris in qapair.sparql.uris if not uris.is_generic()]) > len(
                        set([uris.uri for uris in qapair.sparql.uris if not uris.is_generic()])),
                    [item.uri for item in wrong_entity],
                    [item.uri for item in wrong_relation]]
            if len(wrong_entity) > 0 and len(wrong_relation) > 0:
                stats['general']['-ent_rel'].append(info)
            elif len(wrong_entity) > 0:
                stats['general']['-ent'].append(info)
            elif len(wrong_relation) > 0:
                stats['general']['-rel'].append(info)
            else:
                stats['general']['matched'].append(info)
        else:
            stats['general'].inc('+correct')
            # stats['general']['corrects'].append(qid)
        for k, v in stats.iteritems():
            v.save(os.path.join(args.base_path, 'output', 'stats-{0}.json'.format(k)))

    print stats
