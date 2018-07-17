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
from common.component.chunker.goldChunker import GoldChunker
from difflib import SequenceMatcher


def chunk_cost(ch1, ch2):
    similarity = 0
    l = min(len(ch1), len(ch2))
    if l == 0:
        return 1
    for idx in range(l):
        similarity += SequenceMatcher(None, ch1[idx]['chunk'], ch2[idx]['chunk']).ratio()
    return 1 - (similarity / l)


def linked_cost(dataset, chunks, type, target_uris):
    filtered_dataset = [item for item in dataset if
                        item['chunks'] == chunks
                        and len(item['entities']) > 0
                        and len(item['relations']) > 0]

    uris_with_scores = sorted(
        [uris for item in filtered_dataset for ent_uris in item[type] for uris in ent_uris['uris']],
        key=lambda t: t['confidence'], reverse=True)
    uris = [item['uri'] for item in uris_with_scores]
    uris = sorted(set(uris), key=lambda x: uris.index(x))
    uris_cost = 0
    found_uris = []

    for item in uris:
        if len(target_uris) == 0:
            break
        uris_cost += 1
        if item in target_uris:
            target_uris.remove(item)
            found_uris.append(item)
    if len(target_entities) == 0:
        return uris_cost, found_uris
    else:
        return -uris_cost, found_uris


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run SIB baseline')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset: lcquad, qald", default="lcquad", dest="dataset")
    parser.add_argument("--input", help="input file of Q/A dataset", default="data/LC-QuAD/linked.json", dest="input")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    parser.add_argument("--gold_chunk", help="path to gold chunked dataset", default="data/LC-QuAD/linked_IOB.pk",
                        dest="gold_chunk")
    args = parser.parse_args()

    with open(os.path.join(args.base_path, args.gold_chunk)) as data_file:
        gold_chunker = pk.load(data_file)
        gold_chunker = GoldChunker({item[0]: item[1:] for item in gold_chunker})

    dataset = [{"question": "Name the municipality of Roberto Clemente Bridge ?"}]
    if args.dataset == 'lcquad':
        dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.input))
    elif args.dataset == 'qald':
        dataset = Qald(os.path.join(args.base_path, args.input))

    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    parse_sparql = dataset.parser.parse_sparql
    # pipeline = IQAPipeline(args, kb, parse_sparql)
    oracle = Oracle()
    # linker_evaluator = LinkerEvaluator(GoldLinker())

    pipeline_path = os.path.join(args.base_path, 'output', 'pipeline')
    if not os.path.exists(pipeline_path):
        os.mkdir(pipeline_path)

    stats = Stats()

    with open(os.path.join(args.base_path, 'output', 'wdaqua_core1.pk'), "r") as data_file:
        wdaqua_results = pk.load(data_file)

    qid = ''
    for qapair in tqdm(dataset.qapairs):
        qid = qapair.id
        stats.inc("total")
        if qapair.id not in wdaqua_results:
            continue
        output_path = os.path.join(pipeline_path, ('{0}.pickle'.format(qapair.id)))
        if os.path.exists(output_path):
            with open(os.path.join(pipeline_path, ('{0}.pickle'.format(qapair.id))), 'r') as file_handler:
                outputs = pk.load(file_handler)

            overall_cost = 0
            gold_chunks = gold_chunker.get_phrases(outputs[-1][0])
            target_entities = [uri.uri for uri in qapair.sparql.uris if uri.is_entity()]
            target_relations = [uri.uri for uri in qapair.sparql.uris if uri.is_ontology()]

            chunk_costs = [chunk_cost(gold_chunks, chunks['chunks']) for chunks in outputs[0]]
            chunk_min_idx = min(xrange(len(chunk_costs)), key=chunk_costs.__getitem__)
            overall_cost += chunk_min_idx + 1

            entities_cost, found_entities = linked_cost(outputs[1], outputs[0][chunk_min_idx]['chunks'], 'entities',
                                                        target_entities)
            relations_cost, found_relations = linked_cost(outputs[1], outputs[0][chunk_min_idx]['chunks'], 'relations',
                                                          target_relations)
            if entities_cost < 0:
                entities_cost *= -1
            if relations_cost < 0:
                relations_cost *= -1
            overall_cost += entities_cost + relations_cost

            queries = [query for item in outputs[2] for query in item['queries'] if
                       len([rel for rel in found_relations if rel in query['query']]) == len(found_relations) and
                       len([rel for rel in found_entities if rel in query['query']]) == len(found_entities)]

            queries = sorted(queries, key=lambda t: t['complete_confidence'], reverse=True)
            query_cost = 0
            found = False
            for query in queries:
                query_cost += 1
                if oracle.validate_query(qapair, SPARQL(query['query'], parse_sparql)):
                    found = True
                    break
            overall_cost += query_cost

            if found:
                stats['{}+correct'.format(qapair.id)] = 1
            else:
                stats['{}-incorrect'.format(qapair.id)] = 1

            stats[qapair.id] = overall_cost
            stats['{}_chunk'.format(qapair.id)] = chunk_min_idx
            stats['{}_entities'.format(qapair.id)] = entities_cost
            stats['{}_relations'.format(qapair.id)] = relations_cost
            stats['{}_queries'.format(qapair.id)] = query_cost
        # if stats["total"] > 100:
        #     break

    stats.save(os.path.join(args.base_path, 'output', 'stats-SIB.json'))
