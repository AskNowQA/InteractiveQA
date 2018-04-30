from common.parser.lc_quad_linked import LC_Qaud_Linked
import argparse, os, json
import matplotlib.pyplot as plt
import numpy as np

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
             'AO-P', 'SO-P']
    x = range(len(json_data))
    y_values = [len([v for v in value if '+' in v]) for key, value in json_data.iteritems()]
    print y_values

    fig = plt.figure()

    ax = fig.add_subplot(231)
    complexity_dist = np.unique(question_complexities[:total], return_counts=True)
    ax.bar(complexity_dist[0], complexity_dist[1])
    ax.title.set_text('Comp. Dist. of: {}'.format(total))

    y_values = np.array([[v for k, v in json_data[key].iteritems() if 'c' not in k] for key in files])
    for idx in range(2, 7):
        current_y_values = y_values[:, np.where(question_complexities[:total] == idx)].reshape(6, -1)

        ax = fig.add_subplot(230 + idx)
        ax.errorbar(x, np.mean(current_y_values, axis=1), np.std(y_values, axis=1), linestyle='None', marker='^')
        plt.xticks(x, files, rotation='vertical')
        ax.title.set_text('Q. Comp.: {}'.format(idx))

    print "diff"
    for item in set([key for __name in files for key in json_data[__name].keys()]):
        try:
            if len(set([json_data[file_name][item] for file_name in files])) > 1:
                # print item, [json_data[file_name][item] for file_name in files]
                pass
        except:
            print item

    plt.show()
