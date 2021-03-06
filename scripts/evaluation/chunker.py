from common.utility.utils import Utils
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.classifierChunkParser import ClassifierChunkParser
from common.component.chunker.goldChunker import GoldChunker
import pickle as pk
import nltk
import os

if __name__ == "__main__":
    test_sentence = "Was winston churchill the prime minister of Selwyn Lloyd?"
    test_sentence = "What is the hometown of Nader Guirat, where Josef Johansson was born too?"
    base_dir = "../../"
    model_dir = os.path.join(base_dir, "models")
    Utils.makedirs(model_dir)
    with open('../../data/LC-QUAD/linked_IOB.pk') as data_file:
        orginal_dataset = pk.load(data_file)

    dataset = [item[1:] for item in orginal_dataset]
    idx = int(len(dataset) * 0.9)
    # idx = -1
    train_sents = dataset[:idx]
    test_sents = dataset[idx + 1:]
    test_sents_tree = [nltk.chunk.conlltags2tree(item) for item in test_sents]

    gold_chunker = GoldChunker({item[0]: item[1:] for item in orginal_dataset})
    print("\nGold Chunker")
    print(gold_chunker.evaluate(test_sents_tree))

    SENNA_chunker = SENNAChunker()
    print("SENNA Chunker")
    print(SENNA_chunker.evaluate(test_sents_tree))

    tagger_filename = os.path.join(model_dir, "ClassifierChunkParser.tagger.model")
    # if os.path.exists(tagger_filename):
    #     os.remove(tagger_filename)

    classifier_chunker = ClassifierChunkParser(train_sents, tagger_filename)
    print("\nClassifier Chunker")
    print(classifier_chunker.evaluate(test_sents_tree))

    print(gold_chunker.get_phrases(test_sentence))
    print(SENNA_chunker.get_phrases(test_sentence))
    print(classifier_chunker.get_phrases(test_sentence))
