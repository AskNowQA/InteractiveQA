from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse, os, json
import matplotlib.pyplot as plt
import numpy as np


def parse_int(val):
    return int(''.join(c for c in val if c.isdigit()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot evaluation qa_results')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset", default="data/LC-QuAD/linked.json", dest="dataset")
    args = parser.parse_args()

    max_k = 200

    dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.dataset))
    question_complexities = np.array(
        [len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())]) for qapair in
         dataset.qapairs])

    output_path = os.path.join(args.base_path, 'output')
    json_data = dict()
    for item in os.listdir(output_path):
        file_name = os.path.join(output_path, item)
        if item.startswith('stats') and file_name.endswith(".json") and 'general' not in item:
            with open(file_name, "r") as data_file:
                json_data[''.join([c for c in item[10:-5] if not c.islower()])] = json.load(data_file)

    with open(os.path.join(output_path, 'stats-general.json'), "r") as data_file:
        total = json.load(data_file)['total']

    files = ['AO-IG', 'SO-IG',
             'AO-OG', 'SO-OG',
             # 'AO-P', 'SO-P',
             'SO-RQ']
    x = range(len(files))
    y_values = [[key, len([v for v in value if '+correct' in v])] for key, value in json_data.iteritems()]
    print '# corrects in strategies', y_values

    number_of_corrects = max(y_values)

    correct_dist = []
    correct_dist_top_k = [[] for k in range(max_k)]

    y_values = [[parse_int(k), 1 if '+correct' in k else 0, json_data[number_of_corrects[0]][str(parse_int(k))]] for
                k, v in json_data[number_of_corrects[0]].iteritems() if 'c' in k]
    y_values.sort()

    number_of_corrects = number_of_corrects[1]
    number_of_tries = np.array([items[2] for items in y_values])
    y_values = np.array([items[1] for items in y_values], dtype=float)
    for idx in range(2, 6):
        correct_dist_in_current_complexity = y_values[np.where(question_complexities[:total] == idx)]
        correct_dist.append(np.sum(correct_dist_in_current_complexity))
        for k in range(max_k):
            number_of_tries_in_current_complexity = number_of_tries[np.where(question_complexities[:total] == idx)]
            correct_dist_top_k[k].append(
                np.sum((correct_dist_in_current_complexity == 1) & (number_of_tries_in_current_complexity <= k)))

    print 'correct_dist', correct_dist, sum(correct_dist)
    fig = plt.figure()
    ax = fig.add_subplot(231)
    complexity_dist = np.unique(question_complexities[:total], return_counts=True)
    ax.bar(complexity_dist[0] - 0.1, complexity_dist[1], color='red', width=0.2, label='Total')
    ax.bar(complexity_dist[0] + 0.1, correct_dist, color='green', width=0.2, label='IQA-All Query')
    ax.bar(complexity_dist[0] + 0.3, correct_dist_top_k[0], color='blue', width=0.2, label='IQA-No Interaction')
    plt.xticks(complexity_dist[0], np.arange(2, 7, 1))
    plt.yticks(np.arange(0, number_of_corrects * 2 / 2, 10))
    ax.title.set_text('Comp. Dist. of: {}/{}\n'.format(number_of_corrects, total))
    ax.legend(loc='upper right')

    ax = fig.add_subplot(232)
    complexity_dist = np.unique(question_complexities[:total], return_counts=True)
    for k in range(7):
        ax.bar(complexity_dist[0] * 1 + 0.1 * k - 0.5, correct_dist_top_k[k], width=0.1,
               label='#{} of interactions'.format(k))
    plt.xticks(complexity_dist[0] * 1, np.arange(2, 7, 1))
    plt.yticks(np.arange(0, number_of_corrects * 2 / 2, 10))
    ax.title.set_text('IQA-Ranking Model'.format(number_of_corrects, total))
    # ax.legend(loc='upper')

    # Ignore correct/incorrect items
    y_values = [[[int(k), v] for k, v in json_data[key].iteritems() if 'c' not in k] for key in files]
    for item in y_values:
        item.sort()
    y_values = [[items[1] for items in line] for line in y_values]
    y_values = np.array(y_values, dtype=float)
    corrects_in_complexity = []
    for idx in range(2, 6):
        current_y_values = y_values[:, np.where(question_complexities[:total] == idx)].reshape(len(files), -1)

        current_y_values[current_y_values == 0] = np.nan

        ax = fig.add_subplot(231 + idx)
        ax.errorbar(x, np.nanmean(current_y_values, axis=1), np.nanstd(y_values, axis=1), linestyle='None', marker='^')
        plt.xticks(x, files, rotation='vertical')
        ax.title.set_text('Q. Comp.: {}'.format(idx))
        plt.yticks(np.arange(0, 56, step=10))
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
