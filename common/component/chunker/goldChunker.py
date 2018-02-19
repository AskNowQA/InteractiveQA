from chunker import Chunker
import nltk


class GoldChunker(Chunker):
    def __init__(self, dataset):
        self.dataset = dataset

    def parse(self, tagged_sent):
        words = [word[0] for word in tagged_sent]
        for item in self.dataset.values():
            if [annotation[0] for annotation in item] == words:
                return nltk.chunk.conlltags2tree(item)

    def shallow_parse(self, text):
        if text in self.dataset:
            return [[item[0], item[2]] for item in self.dataset[text]]
        return None
