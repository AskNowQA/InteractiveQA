from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse, os, json
import matplotlib.pyplot as plt
import numpy as np


def parse_int(val):
    return int(''.join(c for c in val if c.isdigit()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot evaluation results')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset", default="data/LC-QuAD/linked.json", dest="dataset")
    args = parser.parse_args()

    dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.dataset))
    question_complexities = np.array([len([uri for uri in qapair.sparql.uris if not uri.is_generic()]) for qapair in
                                      dataset.qapairs])

    output_path = os.path.join(args.base_path, 'output')
    json_data = dict()
    for item in os.listdir(output_path):
        file_name = os.path.join(output_path, item)
        if file_name.endswith(".json") and 'general' not in item:
            with open(file_name, "r") as data_file:
                json_data[''.join([c for c in item[10:-5] if not c.islower()])] = json.load(data_file)

    with open(os.path.join(output_path, 'stats-general.json'), "r") as data_file:
        total = json.load(data_file)['total']

    files = ['AO-IG', 'SO-IG',
             'AO-OG', 'SO-OG',
             'AO-P', 'SO-P',
             'SO-RQ']
    x = range(len(json_data))
    y_values = [len([v for v in value if '+correct' in v]) for key, value in json_data.iteritems()]
    print y_values

    number_of_corrects = y_values[0]

    correct_dist = []
    y_values = [[[parse_int(k), 1 if '+correct' in k else 0] for k, v in json_data[key].iteritems() if 'c' in k] for key
                in files]
    for item in y_values:
        item.sort()
    y_values = [[items[1] for items in line] for line in y_values]
    y_values = np.array(y_values, dtype=float)
    for idx in range(2, 7):
        current_y_values = y_values[:, np.where(question_complexities[:total] == idx)].reshape(len(files), -1)
        correct_dist.append(np.sum(current_y_values, 1)[0])

    print correct_dist, sum(correct_dist)
    fig = plt.figure()
    ax = fig.add_subplot(231)
    complexity_dist = np.unique(question_complexities[:total], return_counts=True)
    ax.bar(complexity_dist[0] - 0.1, complexity_dist[1], color='red', width=0.2)
    ax.bar(complexity_dist[0] + 0.1, correct_dist, color='green', width=0.2)
    plt.xticks(complexity_dist[0], np.arange(2, 7, 1))
    plt.yticks(np.arange(0, 150, step=20))
    ax.title.set_text('Comp. Dist. of: {}/{}'.format(number_of_corrects, total))

    # Ignore correct/incorrect items
    y_values = [[[int(k), v] for k, v in json_data[key].iteritems() if 'c' not in k] for key in files]
    for item in y_values:
        item.sort()
    y_values = [[items[1] for items in line] for line in y_values]
    y_values = np.array(y_values, dtype=float)
    corrects_in_complexity = []
    for idx in range(2, 7):
        current_y_values = y_values[:, np.where(question_complexities[:total] == idx)].reshape(len(files), -1)

        current_y_values[current_y_values == 0] = np.nan

        ax = fig.add_subplot(230 + idx)
        ax.errorbar(x, np.nanmean(current_y_values, axis=1), np.nanstd(y_values, axis=1), linestyle='None', marker='^')
        plt.xticks(x, files, rotation='vertical')
        ax.title.set_text('Q. Comp.: {}'.format(idx))
        plt.yticks(np.arange(-5, 31, step=5))
        print np.nanmean(current_y_values, axis=1)

    print "diff"
    for item in set([key for __name in files for key in json_data[__name].keys()]):
        try:
            if len(set([json_data[file_name][item] for file_name in files])) > 1:
                # print item, [json_data[file_name][item] for file_name in files]
                pass
        except:
            print item

    plt.show()
