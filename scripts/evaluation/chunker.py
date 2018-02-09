import pickle as pk
import nltk
from common.component.chunker.SENNAChunker import SENNAChunker

if __name__ == "__main__":
    with open('../../data/LC-QUAD/linked2843_IOB.pk') as data_file:
        dataset = pk.load(data_file)
    idx = int(len(dataset) * 0.9)
    idx = -1
    train_sents = dataset[:idx]
    test_sents = dataset[idx + 1:]
    test_sents = [nltk.chunk.conlltags2tree(item) for item in test_sents]

    chunker = SENNAChunker()
    print chunker.evaluate(test_sents)
    print chunker.shallowParse("Was Winston Churchill the prime minister of Selwyn Lloyd?")
