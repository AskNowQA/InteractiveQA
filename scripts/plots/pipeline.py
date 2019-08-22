from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse, os, json
import matplotlib.pyplot as plt
import numpy as np
import pickle as pk
import matplotlib

labels = {'SO-RQ': 'NIB-IQA', 'SO-IG': 'IQA-IG', 'SO-OG': 'IQA-OG', '': 'SIB'}
colors = {'NIB-IQA': 'green', 'IQA-IG': 'blue', 'IQA-OG': 'orange', 'SIB': 'red', 'NIB-WDAqua': 'brown',
          'NIB-IQA-Top1': 'blue'}

font = {'size': 14}
matplotlib.rc('font', **font)


def extract_id(val):
    if '-' in val:
        idx = val.index('-')
    else:
        idx = val.index('+')
    return val[:idx]


def comp_dist(complexity_dist, number_of_corrects):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(list(complexity_dist[0]), complexity_dist[1], color='gray')
    for i, v in enumerate(complexity_dist[1]):
        ax.text(i + 1.9, v + 10, str(v), color='black')

    plt.xticks(complexity_dist[0], complexity_dist[0])
    plt.yticks(np.arange(0, number_of_corrects * 2 / 2, 100))
    fig.tight_layout()
    plt.savefig('comp_dist.png')


def a_r1_wd(correct_dist, complexity_dist, correct_dist_top_k, wd_perf):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    y_ratio = 100 * (correct_dist / np.array(complexity_dist[1], dtype=float))
    ax.bar(complexity_dist[0] - 0.2, y_ratio, color=colors['NIB-IQA'], label='NIB-IQA', width=0.2)
    for i, v in enumerate(y_ratio):
        ax.text(i + 1.7, v + 1, str(int(v)) + '%', color='black')

    y_ratio = 100 * (correct_dist_top_k[0] / np.array(complexity_dist[1], dtype=float))
    ax.bar(complexity_dist[0], y_ratio, color=colors['NIB-IQA-Top1'], label='NIB-IQA-Top1', width=0.2)
    for i, v in enumerate(y_ratio):
        ax.text(i + 1.9, v + 1, str(int(v)) + '%', color='black')

    wd_f1 = [wd_perf[str(item)][2] * 100 for item in complexity_dist[0]]
    ax.bar(complexity_dist[0] + 0.2, wd_f1, color=colors['NIB-WDAqua'], width=0.2, label='NIB-WDAqua')
    for i, v in enumerate(wd_f1):
        ax.text(i + 2.1, v + 1, str(int(v)) + '%', color='black')

    # ax.set_xscale('log')
    plt.xticks(complexity_dist[0], complexity_dist[0])
    plt.yticks(np.arange(0, 101, 5))
    ax.legend(loc='upper left')
    fig.tight_layout()
    plt.savefig('a-r1-wd.png')


def inter_inc_f1(complexity_dist, correct_dist_top_k, complexity_index, wd_perf):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for file in correct_dist_top_k.keys():
        ax.plot(100.0 * correct_dist_top_k[file][:, complexity_index] / complexity_dist[1][complexity_index],
                label=labels[file], color=colors[labels[file]])
    ax.plot([wd_perf[str(complexity_index + 2)][2] * 100] * len(correct_dist_top_k['']), label='NIB-WDAqua',
            color=colors['NIB-WDAqua'])
    plt.yticks(np.arange(0, 101, 10))
    ax.set_xscale("log", nonposy='clip')
    ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.xaxis.set_minor_formatter(matplotlib.ticker.ScalarFormatter())
    ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(subs=[50, 200]))
    if complexity_index == 1:
        ax.legend(loc='upper right')
    fig.tight_layout()
    plt.savefig('inter_inc_f1_{}.png'.format(complexity_index + 2))


def succ_rate(files, json_data, comp_range, question_complexities):
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

        y_ratios = correct_complexities[1] * 100 / np.array(all_complexities[1], dtype=float)
        ax.bar(correct_complexities[0] + (counter * 0.1) - 0.2, y_ratios, width=0.1, label=labels[file_id],
               color=colors[labels[file_id]])

        for i, v in enumerate(y_ratios):
            ax.text(i + 1.8 + (counter * 0.1), v + 5, str(int(v)), color='black', rotation='vertical')

        counter += 1

    plt.xticks(comp_range, comp_range)
    plt.yticks(np.arange(0, 101, 10))
    ax.legend(loc='upper right')
    fig.tight_layout()
    plt.savefig('succ_rate.png')


def inter_cost(files, json_data, comp_range, question_complexities):
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
        ax.bar(comp_range + (counter * 0.1) - 0.2, res[:, 0], width=0.1, label=labels[file_id],
               color=colors[labels[file_id]])
        ax.errorbar(comp_range + (counter * 0.1) - 0.2, res[:, 0], res[:, 1], linestyle='None', marker='^',
                    color=colors[labels[file_id]])
        print(labels[file_id], res[:, 0])
        counter += 1

    ax.set_yscale("log", nonposy='clip')
    plt.xticks(comp_range, comp_range)
    ax.legend(loc='upper right', ncol=2)
    fig.tight_layout()
    plt.savefig('inter_cost.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot evaluation qa_results')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    parser.add_argument("--dataset", help="input Q/A dataset", default="data/LC-QuAD/linked.json", dest="dataset")
    args = parser.parse_args()

    max_k = 200

    dataset = LC_Qaud_Linked(os.path.join(args.base_path, args.dataset))
    with open(os.path.join(args.base_path, 'output', 'wdaqua_core1.pk'), "rb") as data_file:
        wdaqua_results = pk.load(data_file)

    with open(os.path.join(args.base_path, 'output', 'wd_perf.json'), "r") as data_file:
        wd_perf = json.load(data_file)

    with open(os.path.join(args.base_path, 'output', 'stats-SIB.json'), "r") as data_file:
        question_cadidate_queries = json.load(data_file)

    ranges = np.array(list(map(int, np.logspace(0, 4, num=10))))
    # ranges = ranges[ranges < 3500]

    # question_complexities = {
    #     qapair.id: [r for idx, r in enumerate(ranges) if question_cadidate_queries[qapair.id + '_candidate_queries']<r][0] for
    #     qapair in dataset.qapairs if qapair.id in wdaqua_results}

    question_complexities = {
        qapair.id: len([uri for uri in qapair.sparql.uris if not (uri.is_generic() or uri.is_type())]) for
        qapair in dataset.qapairs if qapair.id in wdaqua_results}

    output_path = os.path.join(args.base_path, 'output')
    json_data = dict()
    for item in os.listdir(output_path):
        file_name = os.path.join(output_path, item)
        if item.startswith('stats') and file_name.endswith(".json") and 'general' not in item and 'tmp' not in item:
            with open(file_name, "r") as data_file:
                json_data[''.join([c for c in item[10:-5] if not c.islower()])] = json.load(data_file)

    # with open(os.path.join(output_path, 'stats-general.json'), "r") as data_file:
    #     total = json.load(data_file)['total']
    total = len(question_complexities)

    files = [  # 'AO-IG',
        'SO-IG',
        # 'AO-OG',
        'SO-OG',
        # 'AO-P', 'SO-P',
        'SO-RQ',
        '']
    x = range(len(files))
    y_values = [[key, len([v for v in value if '+correct' in v])] for key, value in json_data.items()]
    print('# corrects in strategies', y_values)

    number_of_corrects = max(y_values)
    # comp_range = np.arange(2, 6, 1)

    # question_complexities = {k: v for k, v in question_complexities.iteritems() if k in y_values[:, 0]}
    complexity_dist = np.unique(list(question_complexities.values()), return_counts=True)
    comp_range = complexity_dist[0]
    correct_dist_top_k = {}
    correct_dist = {}
    for f_id in files:
        correct_dist_top_k[f_id] = [[] for k in range(max_k)]
        y_values = np.array([[extract_id(k), '+correct' in k, v] for k, v in json_data[f_id].items() if
                             'cor' in k], dtype=object)
        y_values = np.array([[k, m, json_data[f_id][k], question_complexities[k]] for k, m, v in y_values],
                            dtype=object)

        correct_dist[f_id] = []
        for idx in comp_range:
            correct_items_in_current_complexity = [item for item in y_values if item[1] and item[3] == idx]

            correct_dist[f_id].append(len(correct_items_in_current_complexity))
            for k in range(max_k):
                number_of_tries_in_current_complexity = np.array(
                    [item[2] for item in correct_items_in_current_complexity])
                correct_dist_top_k[f_id][k].append(np.sum((number_of_tries_in_current_complexity <= k)))
        correct_dist_top_k[f_id] = np.array(correct_dist_top_k[f_id])

    print('correct_dist', correct_dist, {k: sum(v) for k, v in correct_dist.items()})

    for k, v in correct_dist.items():
        correct_dist[k] = np.array(correct_dist[k])

    comp_dist(complexity_dist, number_of_corrects[1])
    a_r1_wd(correct_dist[number_of_corrects[0]], complexity_dist, correct_dist_top_k[number_of_corrects[0]], wd_perf)
    # for i in range(4):
    #     inter_inc_f1(complexity_dist, correct_dist_top_k, i, wd_perf)
    # succ_rate(files, json_data, comp_range, question_complexities)
    # inter_cost(files, json_data, comp_range, question_complexities)
