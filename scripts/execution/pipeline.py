from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.goldChunker import GoldChunker
from common.component.linker.earl import EARL
from common.component.query.sqg import SQG
from common.container.interactionOptions import InteractionOptions
from common.parser.lc_quad_linked import LC_Qaud_Linked
from common.evaluation.oracle import Oracle
from tqdm import tqdm
import argparse
import pickle as pk
import os


class IQAPipeline:
    def __init__(self, args):
        classifier_chunker = ClassifierChunkParser([], os.path.join(args.base_path, args.model))
        SENNA_chunker = SENNAChunker()
        with open(os.path.join(args.base_path, args.gold_chunk)) as data_file:
            gold_chunk_dataset = pk.load(data_file)
        gold_Chunker = GoldChunker({item[0]: item[1:] for item in gold_chunk_dataset})
        self.__chunkers = [classifier_chunker, SENNA_chunker, gold_Chunker]
        earl = EARL(cache_path=os.path.join(args.base_path, "caches/"), use_cache=True)
        self.__linkers = [earl]
        sqg = SQG(cache_path=os.path.join(args.base_path, "caches/"), use_cache=False)
        self.__query_builders = [sqg]

        self.components = [self.__chunk, self.__link, self.__build_query]

    def __build_query(self, prev_output):
        outputs = [qb.build_query(prev_output["question"], prev_output["entities"], prev_output["relations"]) for qb in
                   self.__query_builders]
        for output in outputs:
            output["entities"] = prev_output["entities"]
            output["relations"] = prev_output["relations"]
            output["question"] = prev_output["question"]
            output["chunks"] = prev_output["chunks"]
            for query in output["queries"]:
                _, _, uris = dataset.parser.parse_sparql(query["query"])
                confidence = 1
                for uri in uris:
                    if uri.is_generic():
                        continue
                    raw_uri = uri.raw_uri.strip("<>")
                    found = False
                    for item in prev_output["entities"][0]["uris"]:
                        if item["uri"] == raw_uri:
                            confidence *= item["confidence"]
                            found = True
                            break
                    if not found:
                        for item in prev_output["relations"][0]["uris"]:
                            if item["uri"] == raw_uri:
                                confidence *= item["confidence"]
                                break
                confidence *= query["confidence"]
                query["complete_confidence"] = confidence
        return outputs

    def __link(self, prev_output):
        chunks = [item["chunk"] for item in prev_output["chunks"]]
        outputs = [item.link_entities_relations(prev_output["question"], chunks) for item in self.__linkers]
        for item in outputs:
            item["question"] = prev_output["question"]
            item["chunks"] = prev_output["chunks"]
        return outputs

    def __chunk(self, question):
        chunkers_output = [chunker.get_phrases(question) for chunker in self.__chunkers]
        return [{"question": question, "chunks": item} for item in chunkers_output]

    def run(self, dataset):
        oracle = Oracle()
        for qapair in tqdm(dataset.qapairs):
            if 'municipality' not in qapair.question.text:
                continue
            outputs = {-1: [qapair.question.text]}
            for cmpnt_idx, component in enumerate(self.components):
                outputs[cmpnt_idx] = []
                for prev_output in outputs[cmpnt_idx - 1]:
                    outputs[cmpnt_idx].extend(component(prev_output))

            interaction_options = InteractionOptions(outputs[2], dataset.parser.parse_sparql)
            while interaction_options.has_interaction():
                io_idx = interaction_options.interactionWithMaxInformationGain()
                interaction_options.update(io_idx, oracle.answer(io_idx))
            # if any([len(item['queries']) > 0 for item in outputs[cmpnt_idx]]):
            #     for item in outputs:
            #         print outputs[item]

            # print "*" * 20


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
    pipeline = IQAPipeline(args)
    pipeline.run(dataset)
