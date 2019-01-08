from common.pipeline import IQAPipeline
from common.kb.dbpedia import DBpedia
from common.container.qapair import QApair
from common.parser.lc_quad_linked import LC_Qaud_LinkedParser
from common.interaction.interactionManager import InteractionManager

import os
import argparse
import time
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--base_path", help="base path", default="../", dest="base_path")
    parser.add_argument("--model", help="path to model", default="models/ClassifierChunkParser.tagger.model",
                        dest="model")
    args = parser.parse_args()
    kb = DBpedia(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
    parse_sparql = LC_Qaud_LinkedParser().parse_sparql
    pipeline = IQAPipeline(args, kb, parse_sparql)

    start_time = time.time()
    qa_pair = QApair('who is the leader of Germany?', '', '', 'id', LC_Qaud_LinkedParser())
    outputs, num_pipelines = pipeline.run(qa_pair)
    last_len = 0
    while last_len < num_pipelines:
        time.sleep(0.5)
        if len(outputs.queue) > last_len:
            last_len = len(outputs.queue)
            print(last_len, time.time() - start_time)

    outputs = [item for output in outputs.queue for item in output[2]]
    interaction_types = [[False, True], [True, True]]
    interaction_data = InteractionManager(outputs, kb=kb,
                                          sparql_parser=parse_sparql,
                                          interaction_type=interaction_types,
                                          strategy='InformationGain',
                                          target_query=None)
    io, query = interaction_data.get_interaction_option()
    print(io)
    finish_time = time.time()
    print(finish_time - start_time)
