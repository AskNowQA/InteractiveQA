import os
import nltk
from collections import Iterable
import sklearn
from common.component.chunker.chunker import Chunker


def features(tokens, index, history):
    """
    `tokens`  = a POS-tagged sentence [(w1, t1), ...]
    `index`   = the index of the token we want to extract features for
    `history` = the previous predicted IOB tags
    """

    stemmer = nltk.stem.snowball.SnowballStemmer('english')

    tokens = [('__START2__', '__START2__'), ('__START1__', '__START1__')] + list(tokens) + [
        ('__END1__', '__END1__'),
        ('__END2__', '__END2__')]
    history = ['__START2__', '__START1__'] + list(history)

    index += 2

    word, pos = tokens[index]
    prevword, prevpos = tokens[index - 1]
    prevprevword, prevprevpos = tokens[index - 2]
    nextword, nextpos = tokens[index + 1]
    nextnextword, nextnextpos = tokens[index + 2]

    return {
        'word': word,
        'lemma': stemmer.stem(word),
        'pos': pos,

        'next-word': nextword,
        'next-pos': nextpos,

        'next-next-word': nextnextword,
        'nextnextpos': nextnextpos,

        'prev-word': prevword,
        'prev-pos': prevpos,

        'prev-prev-word': prevprevword,
        'prev-prev-pos': prevprevpos,
    }


class ClassifierChunkParser(Chunker):
    def __init__(self, chunked_sents, tagger_filename, **kwargs):
        if os.path.exists(tagger_filename):
            self.tagger = sklearn.externals.joblib.load(tagger_filename)
        else:
            assert isinstance(chunked_sents, Iterable)

            def triplets2tagged_pairs(iob_sent):
                return [((word, pos), chunk) for word, pos, chunk in iob_sent]

            chunked_sents = [triplets2tagged_pairs(sent) for sent in chunked_sents]

            # ClassifierBasedPOSTagger, ClassifierBasedTagger, UnigramTagger, BigramTagger
            self.tagger = nltk.ClassifierBasedTagger(
                train=chunked_sents,
                feature_detector=features,
                **kwargs)
            sklearn.externals.joblib.dump(self.tagger, tagger_filename)

    def parse(self, tagged_sent):
        chunks = self.tagger.tag(tagged_sent)
        iob_triplets = [(w, t, c) for ((w, t), c) in chunks]
        return nltk.chunk.conlltags2tree(iob_triplets)

    def shallow_parse(self, sentence):
        tagged_sent = nltk.pos_tag(nltk.word_tokenize(sentence))
        chunks = self.tagger.tag(tagged_sent)
        return [(item[0][0], item[1]) for item in chunks]
