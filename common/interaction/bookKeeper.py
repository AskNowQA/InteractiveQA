from random import randint


class BookKeeper:
    def __init__(self):
        pass

    def new_question(self, userid):
        # return 'fb1bfcc7943943b892d6d22690b2ef48'
        questions = ['81218ea48e2f44a1bef8c118ae5b965a', '8216e5b6033a407191548689994aa32e',
                     '6ac000fc0bb7458f8556f603ed42e4b3', 'dad51bf9d0294cac99d176aba17c0241',
                     '48584c830439478e9272821ca6fac246', '339f9ccfb682456ab0f1e7f580a2d27e',
                     '2a11aeb11ce248cfaf63be2b6701fe9a', '5df6285e711048a5aa9d59ee7bbc7886',
                     '54e823bdc8d44ed7a0a40c77e29c361d', '62fc3395a7ce4c27ba5bfb82e020dab6',
                     '32ab0f92ca6444c5a2877e23fc76303c', 'df8a83a06ca941c3b6f30667a64bc305',
                     'ce216d620d154f13814dd2f6b967c292', '4447f7daa7cf45eaadac04711dce299a',
                     '9a7523469c8c45b58ec65ed56af6e306', 'd87c7466bde24cb3a5fcc03dc0c210fe',
                     '6ff03a568e2e4105b491ab1c1411c1ab', '5e3b1b3d67c14e79a69346483e72f30e',
                     '93ca4dc34b5e4bf7ba90d0ae55f7d50c', 'f76953f003c2433d837966593c777c75',
                     'a6ff1c4c6e0f4b519d1f50c706af5469', '30b709079ea5421cb33c227c3feb9019',
                     'fb1bfcc7943943b892d6d22690b2ef48', '1be4e465a7ac4a6c893e6b1fc1aef01a',
                     '3f943b9b68fe43c7a7363ff39f9f3074', '09b0e80486e44ea2b1cbca4f69c89923',
                     'd101acb6da7a464cbdec88d18d5b855e', '082ecdc0056f4f3192e3b13e46d0ee0c',
                     '42d9e558edd840a0a310036f7f9bb9b2', '312435fad0194831a80fe3346c9a683b',
                     'a649a19bfcbc4f2e962d2199f8e9598d', 'f0a9f1ca14764095ae089b152e0e7f12',
                     '78435963a0b241ecbd9b7ab9e4916acc', 'e7c8927b5bec41c6a09ea2319c24e65f',
                     '418b062f88884aff8095211e8c44cbed', '556d585ed3d04cff978e0f6c86b73d8d',
                     'a969284fc29d4b659e9088088a2c49f2', 'a899e312823543e7b728a2517d29392d',
                     '80d88d56a6634b49b41ded0bdc54ae5c', '873c3fe1ec484dcfbb114320042f298d']
        return questions[randint(0, len(questions) - 1)]


if __name__ == '__main__':
    import os, pickle

    path = '../../output/pipeline/'
    queries = []
    for file_name in os.listdir(path):
        with open(os.path.join(path, file_name), 'r') as fh:
            result = pickle.load(fh)
            if len(result[2]) > 0:
                queries.append(file_name)
    print queries
