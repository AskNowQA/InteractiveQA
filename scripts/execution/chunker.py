from common.utility.utils import Utils
from common.component.chunker.SENNAChunker import SENNAChunker
from common.component.chunker.classifierChunkParser import ClassifierChunkParser
import pickle as pk
import nltk
import os
import sys
import logging
import argparse

if __name__ == "__main__":

    test_sentence = "Was winston Churchill the prime minister of Selwyn Lloyd?"

    logger = logging.getLogger(__name__)
    Utils.setup_logging()

    parser = argparse.ArgumentParser(description='Run chunker')
    parser.add_argument("--input", help="input dataset", default="../../data/LC-QUAD/linked2843_IOB.pk", dest="input")
    parser.add_argument("--output", help="linker output path", default="../../data/LC-QuAD/EARL/output_nltk.json",
                        dest="output")
    parser.add_argument("--model", help="path to model", default="../../models/ClassifierChunkParser.tagger.model",
                        dest="model")
    args = parser.parse_args()

    if not (os.path.exists(args.input) and os.path.exists(args.model)):
        logger.error("Input or model files doesn't exist.")
        sys.exit(0)

    classifier_chunker = ClassifierChunkParser([], args.model)
    print(classifier_chunker.get_phrases(test_sentence))
