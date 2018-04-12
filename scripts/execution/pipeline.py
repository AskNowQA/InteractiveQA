from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.linker.earl import EARL
from common.component.query.sqg import SQG
from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pipeline')
    parser.add_argument("--input", help="input dataset", default="../../data/LC-QUAD/linked2843_IOB.pk", dest="input")
    parser.add_argument("--model", help="path to model", default="../../models/ClassifierChunkParser.tagger.model",
                        dest="model")
    args = parser.parse_args()

    dataset = [{"question": "Name the municipality of Roberto Clemente Bridge ?"}]
    dataset = LC_Qaud_Linked("../../data/LC-QuAD/linked.json")

    classifier_chunker = ClassifierChunkParser([], args.model)
    SENNA_chunker = SENNAChunker()


    def chunkers(question):
        output1 = classifier_chunker.get_phrases(question)
        output2 = SENNA_chunker.get_phrases(question)
        return [{"question": question, "chunks": output1}, {"question": question, "chunks": output2}]


    earl = EARL(use_cache=False)


    def linkers(prev_output):
        chunks = [item["chunk"] for item in prev_output["chunks"]]
        output = earl.link_entities_relations(prev_output["question"], chunks)
        output["question"] = prev_output["question"]
        output["chunks"] = prev_output["chunks"]
        return [output]


    sqg = SQG(use_cache=False)


    def query_builders(prev_output):
        output = sqg.build_query(prev_output["question"], prev_output["entities"], prev_output["relations"])
        output["entities"] = prev_output["entities"]
        output["relations"] = prev_output["relations"]
        output["question"] = prev_output["question"]
        output["chunks"] = prev_output["chunks"]
        for query in output["queries"]:
            # query["confidence"]
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

        return [output]

components = [chunkers, linkers, query_builders]

for qapair in dataset.qapairs:
    outputs = {-1: [qapair.question.text]}
    for cmpnt_idx, component in enumerate(components):
        outputs[cmpnt_idx] = []
        for prev_output in outputs[cmpnt_idx - 1]:
            outputs[cmpnt_idx].extend(component(prev_output))

for item in outputs:
    print outputs[item]
