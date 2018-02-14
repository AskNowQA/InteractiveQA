from common.utility.utils import Utils
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.classifierChunkParser import ClassifierChunkParser
import pickle as pk
import nltk
import os

if __name__ == "__main__":
    test_sentence = "Was Winston Churchill the prime minister of Selwyn Lloyd?"
    base_dir = "../../"
    model_dir = os.path.join(base_dir, "models")
    Utils.makedirs(model_dir)
    with open('../../data/LC-QUAD/linked2843_IOB.pk') as data_file:
        dataset = pk.load(data_file)
    idx = int(len(dataset) * 0.9)
    # idx = -1
    train_sents = dataset[:idx]
    test_sents = dataset[idx + 1:]
    test_sents_tree = [nltk.chunk.conlltags2tree(item) for item in test_sents]

    SENNA_chunker = SENNAChunker()
    print "SENNA Chunker"
    print SENNA_chunker.evaluate(test_sents_tree)


    tagger_filename = os.path.join(model_dir, "ClassifierChunkParser.tagger.model")
    # if os.path.exists(tagger_filename):
    #     os.remove(tagger_filename)

    classifier_chunker = ClassifierChunkParser(train_sents, tagger_filename)
    print "Classifier Chunker"
    # print classifier_chunker.evaluate(test_sents_tree)



    print SENNA_chunker.parse(nltk.pos_tag(nltk.word_tokenize(test_sentence)))
    print classifier_chunker.parse(nltk.pos_tag(nltk.word_tokenize(test_sentence)))
