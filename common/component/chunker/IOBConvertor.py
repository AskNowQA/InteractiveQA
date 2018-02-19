import json
import pickle as pk
import nltk
import argparse
from tqdm import tqdm


class IOBConvertor:
    def __init__(self, file_path):
        self.file_path = file_path

    def convert(self):
        with open(self.file_path) as data_file:
            data_set = json.load(data_file)
        output = []
        for item in tqdm(data_set):
            question = item["question"]

            # nltk.word_tokenize, pos_tag
            tokenized = nltk.word_tokenize(question)
            pos_tag = nltk.pos_tag(tokenized)

            raw_annotations = item["entity mapping"] + item["predicate mapping"]
            for annotation in raw_annotations:
                annotation["seq"] = map(int, annotation["seq"].split(","))
            raw_annotations.sort(key=lambda item: item["seq"][0])
            tokenized_question = ""
            annotations = []
            idx_ann = 0
            idx = 0
            for word in tokenized:
                tokenized_question += word + " "
                if idx_ann < len(raw_annotations):
                    start_index, end_index = raw_annotations[idx_ann]["seq"]
                    if start_index < len(tokenized_question) - 2 <= end_index:
                        token = "B" if token == "O" else "I"
                        token += "-NP" if "resource/" in raw_annotations[idx_ann]["uri"] else "-VP"
                    else:
                        token = "O"
                else:
                    token = "O"

                annotations.append([word, pos_tag[idx][1], token])
                if len(tokenized_question) > end_index:
                    idx_ann += 1
                    token = "O"
                idx += 1

            output.append([question]+annotations)

        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IOB Convertor')
    parser.add_argument("--input", help="Path of input file", default="../../../data/LC-QUAD/linked_full.json",
                        dest="input_path")
    parser.add_argument("--output", help="Path of output file", default="../../../data/LC-QUAD/linked_IOB.pk",
                        dest="output_path")
    args = parser.parse_args()
    print args

    iob = IOBConvertor(args.input_path)
    output = iob.convert()
    with open(args.output_path, 'w') as data_file:
        pk.dump(output, data_file)
