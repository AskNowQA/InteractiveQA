from common.pipeline import IQAPipeline
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.container.interactionOptions import InteractionOptions
from common.evaluation.oracle import Oracle
from common.kb.dbpedia import DBpedia
from common.utility.stats import Stats
from tqdm import tqdm
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset", default="data/LC-QuAD/linked.json", dest="dataset")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked2843_IOB.pk",
                        dest="gold_chunk")
    args = parser.parse_args()

    dataset = [{"question": "Name the municipality of Roberto Clemente Bridge ?"}]
    dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.dataset))

    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    parse_sparql = dataset.parser.parse_sparql
    pipeline = IQAPipeline(args, kb, parse_sparql)
    oracle = Oracle()

    interaction_types = [[False, True], [True, True]]
    strategies = ['InformationGain', 'OptionGain', 'Probability']
    w = 1

    stats = {('IQA-AO' if all(type) else 'IQA-SO') + '-' + strategy: Stats() for strategy in strategies for type
             in interaction_types}
    stats['general'] = Stats()
    qid = -1
    for qapair in tqdm(dataset.qapairs):
        qid += 1
        stats['general'].inc("total")
        # if 'municipality' not in qapair.question.text:
        #     continue
        # if stats['general']['total'] < 4 + 1:
        #     continue
        outputs = pipeline.run(qapair)
        for interaction_type in interaction_types:
            interaction_type_str = 'IQA-AO' if all(interaction_type) else 'IQA-SO'
            for strategy in strategies:
                stats[interaction_type_str + '-' + strategy].inc(str(qid), 0)
                interaction_options = InteractionOptions(outputs[2], kb.parse_uri, parse_sparql, kb, *interaction_type)
                while interaction_options.has_interaction() and \
                        not oracle.validate_query(qapair, interaction_options.queryWithMaxProbability()):

                    if strategy == 'InformationGain':
                        io = interaction_options.interactionWithMaxInformationGain()
                    elif strategy == 'OptionGain':
                        io = interaction_options.interactionWithMaxOptionGain(w)
                    elif strategy == 'Probability':
                        io = interaction_options.interactionWithMaxProbability()

                    interaction_options.update(io, oracle.answer(qapair, io))
                    stats[interaction_type_str + '-' + strategy].inc(str(qid))

                if oracle.validate_query(qapair, interaction_options.queryWithMaxProbability()):
                    stats[interaction_type_str + '-' + strategy].inc(str(qid) + "+correct")
                else:
                    stats[interaction_type_str + '-' + strategy].inc(str(qid) + "-incorrect")

        for k, v in stats.iteritems():
            v.save(os.path.join(args.base_path, 'output', 'stats-{0}.json'.format(k)))

    print stats
