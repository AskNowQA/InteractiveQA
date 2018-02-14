from __future__ import division
from __future__ import print_function
import os
import torch
from vocab import Vocab
from itertools import islice


class Struct(object): pass


class Utils:
    @staticmethod
    def makedirs(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return None

    @staticmethod
    def load_word_vectors(path):
        if os.path.isfile(path + '.pth') and os.path.isfile(path + '.vocab'):
            print('==> File found, loading to memory')
            vectors = torch.load(path + '.pth')
            vocab = Vocab(filename=path + '.vocab')
            return vocab, vectors
        # saved file not found, read from txt file
        # and create tensors for word vectors
        print('==> File not found, preparing, be patient')
        count = sum(1 for line in open(path + '.txt'))
        with open(path + '.txt', 'r') as f:
            contents = f.readline().rstrip('\n').split(' ')
            dim = len(contents[1:])
        words = [None] * (count)
        vectors = torch.zeros(count, dim)
        with open(path + '.txt', 'r') as f:
            idx = 0
            for line in f:
                contents = line.rstrip('\n').split(' ')
                words[idx] = contents[0]
                vectors[idx] = torch.Tensor(list(map(float, contents[1:])))
                idx += 1
        with open(path + '.vocab', 'w') as f:
            for word in words:
                f.write(word + '\n')
        vocab = Vocab(filename=path + '.vocab')
        torch.save(vectors, path + '.pth')
        return vocab, vectors

    @staticmethod
    def build_vocab(filenames, vocabfile):
        vocab = set()
        for filename in filenames:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    for line in f:
                        tokens = line.rstrip('\n').split(' ')
                        vocab |= set(tokens)
        with open(vocabfile, 'w') as f:
            for token in sorted(vocab):
                f.write(token + '\n')

    @staticmethod
    def cat(seq, n):
        return [torch.cat([seq[i][j] for i in range(n)], 0) for j in range(len(seq[0]) - 1)] + [seq[n - 1][-1]]

    @staticmethod
    def window(input, n, cat_=True):
        "Returns a sliding window (of width n) over data from the iterable"
        "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
        seq = [input[0]] * (n - 1) + input

        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield Utils.cat(result, n) if cat_ else result
        for elem in it:
            result = result[1:] + (elem,)
            yield Utils.cat(result, n) if cat_ else result
