from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse, os, json
import matplotlib.pyplot as plt
import numpy as np
import pickle as pk


def extract_id(val):
    if '-' in val:
        idx = val.index('-')
    else:
        idx = val.index('+')
    return val[:idx]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot evaluation qa_results')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset", default="data/LC-QuAD/linked.json", dest="dataset")
    args = parser.parse_args()

    max_k = 200

    dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.dataset))
    with open(os.path.join(args.base_path, 'output', 'wdaqua_core1.pk'), "r") as data_file:
        wdaqua_results = pk.load(data_file)

    question_complexities = {
        qapair.id: len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())]) for
        qapair in dataset.qapairs if qapair.id in wdaqua_results}

    output_path = os.path.join(args.base_path, 'output')
    json_data = dict()
    for item in os.listdir(output_path):
        file_name = os.path.join(output_path, item)
        if item.startswith('stats') and file_name.endswith(".json") and 'general' not in item:
            with open(file_name, "r") as data_file:
                json_data[''.join([c for c in item[10:-5] if not c.islower()])] = json.load(data_file)

    with open(os.path.join(output_path, 'stats-general.json'), "r") as data_file:
        # total = json.load(data_file)['total']
        total = len(question_complexities)

    files = [  # 'AO-IG',
        'SO-IG',
        # 'AO-OG',
        'SO-OG',
        # 'AO-P', 'SO-P',
        'SO-RQ',
        '']
    labels = {'SO-RQ': 'NIB', 'SO-IG': 'IQA-IG', 'SO-OG': 'IQA-OG', '': 'SIB'}
    x = range(len(files))
    y_values = [[key, len([v for v in value if '+correct' in v])] for key, value in json_data.iteritems()]
    print '# corrects in strategies', y_values

    number_of_corrects = max(y_values)
    correct_dist = []
    correct_dist_top_k = [[] for k in range(max_k)]

    y_values = np.array([[extract_id(k), '+correct' in k, v] for k, v in json_data[number_of_corrects[0]].iteritems() if
                         'cor' in k], dtype=object)
    question_complexities = {k: v for k, v in question_complexities.iteritems() if k in y_values[:, 0]}
    complexity_dist = np.unique(question_complexities.values(), return_counts=True)
    comp_range = np.arange(2, 6, 1)

    y_values = np.array([[k, m, json_data[number_of_corrects[0]][k], question_complexities[k]] for k, m, v in y_values],
                        dtype=object)

    number_of_corrects = number_of_corrects[1]
    for idx in range(2, 6):
        correct_items_in_current_complexity = [item for item in y_values if item[1] and item[3] == idx]

        correct_dist.append(len(correct_items_in_current_complexity))
        for k in range(max_k):
            number_of_tries_in_current_complexity = np.array([item[2] for item in correct_items_in_current_complexity])
            correct_dist_top_k[k].append(np.sum((number_of_tries_in_current_complexity <= k)))

    print 'correct_dist', correct_dist, sum(correct_dist)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(complexity_dist[0] - 0.1, complexity_dist[1], color='red', width=0.2, label='NQ-T')
    ax.bar(complexity_dist[0] + 0.1, correct_dist, color='green', width=0.2, label='NQ-A')
    ax.bar(complexity_dist[0] + 0.3, correct_dist_top_k[0], color='blue', width=0.2, label='NQ-R1')
    plt.xticks(complexity_dist[0], np.arange(2, 7, 1))
    plt.yticks(np.arange(0, number_of_corrects * 2 / 2, 100))
    # ax.title.set_text('Comp. Dist. of: {}/{}\n'.format(number_of_corrects, total))
    ax.legend(loc='upper right')
    plt.savefig('comp_dist.png')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for k in range(7):
        ax.bar(complexity_dist[0] * 1 + 0.1 * k - 0.5, correct_dist_top_k[k], width=0.1,
               label='#{} of interactions'.format(k))
    plt.xticks(complexity_dist[0] * 1, np.arange(2, 7, 1))
    plt.yticks(np.arange(0, number_of_corrects * 2 / 5, 50))
    ax.title.set_text('IQA-Ranking Model'.format(number_of_corrects, total))
    # ax.legend(loc='upper')
    plt.savefig('f1_inter_cost.png')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    counter = 0
    for file_id in files:
        correct_complexities = [question_complexities[extract_id(k)] for k, v in json_data[file_id].iteritems() if
                                '+correct' in k]
        all_complexities = [question_complexities[extract_id(k)] for k, v in json_data[file_id].iteritems() if
                            'corr' in k]

        correct_complexities = np.unique(correct_complexities, return_counts=True)
        all_complexities = np.unique(all_complexities, return_counts=True)

        ax.bar(correct_complexities[0] + (counter * 0.1) - 0.2,
               correct_complexities[1] * 100 / np.array(all_complexities[1], dtype=float), width=0.1,
               label=labels[file_id])
        counter += 1

    plt.xticks(comp_range, comp_range)
    plt.yticks(np.arange(0, 101, 10))
    ax.legend(loc='upper right')
    plt.savefig('succ_rate.png')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    counter = 0
    for file_id in files:
        correct_question_id = [extract_id(k) for k, v in json_data[file_id].iteritems()
                               if '+correct' in k or '-incorrect' in k]
        correct_questions = np.array(
            [[question_complexities[q_id], json_data[file_id][q_id]] for q_id in correct_question_id])

        res = []
        for q_c in comp_range:
            question_of_current_comp = np.where(correct_questions[:, 0] == q_c)
            interaction_dist = correct_questions[question_of_current_comp][:, 1]
            res.append([np.nanmean(interaction_dist), np.nanstd(interaction_dist)])
        res = np.array(res)
        ax.bar(comp_range + (counter * 0.1) - 0.2, res[:, 0], width=0.1, label=labels[file_id])
        ax.errorbar(comp_range + (counter * 0.1) - 0.2, res[:, 0], res[:, 1], linestyle='None', marker='^')
        counter += 1

    ax.set_yscale("log", nonposy='clip')
    plt.xticks(comp_range, comp_range)
    ax.legend(loc='upper right')
    # plt.savefig('inter_cost.png')
    fig.show()

    # X-Axis: query complexity, different method
    # Y-Axis is the susses rate

    # # Ignore correct/incorrect items
    # y_values = [[[k, v] for k, v in json_data[key].iteritems() if 'c' not in k] for key in files]
    # y_values = [[items[1] for items in line] for line in y_values]
    # y_values = np.array(y_values, dtype=object)
    # corrects_in_complexity = []
    # for idx in range(2, 6):
    #     current_y_values = y_values[:, np.where(question_complexities[:total] == idx)].reshape(len(files), -1)
    #
    #     current_y_values[current_y_values == 0] = np.nan
    #
    #     ax = fig.add_subplot(231 + idx)
    #     ax.errorbar(x, np.nanmean(current_y_values, axis=1), np.nanstd(y_values, axis=1), linestyle='None', marker='^')
    #     plt.xticks(x, files, rotation='vertical')
    #     ax.title.set_text('Q. Comp.: {}'.format(idx))
    #     plt.yticks(np.arange(0, 56, step=10))
    #     print np.nanmean(current_y_values, axis=1)
    #
    # print "diff"
    # for item in set([key for __name in files for key in json_data[__name].keys()]):
    #     try:
    #         if len(set([json_data[file_name][item] for file_name in files])) > 1:
    #             # print item, [json_data[file_name][item] for file_name in files]
    #             pass
    #     except:
    #         print item
    # plt.show()
