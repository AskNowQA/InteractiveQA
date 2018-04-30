import argparse, os, json
import matplotlib.pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot evaluation results')
    parser.add_argument("--base_path", help="base path", default="../../", dest="base_path")
    args = parser.parse_args()

    output_path = os.path.join(args.base_path, 'output')
    json_data = dict()
    for item in os.listdir(output_path):
        file_name = os.path.join(output_path, item)
        if file_name.endswith(".json") and 'general' not in item:
            with open(file_name, "r") as data_file:
                json_data[item[10:-5]] = json.load(data_file)

    with open(os.path.join(output_path, 'stats-general.json'), "r") as data_file:
        total = float(json.load(data_file)['total'])

    files = ['AO-InformationGain', 'SO-InformationGain',
             'AO-OptionGain', 'SO-OptionGain',
             'AO-Probability', 'SO-Probability']
    x = range(len(json_data))
    y_values = [len([v for v in value if '+' in v]) for key, value in json_data.iteritems()]
    print y_values

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax1.title.set_text('# of correctly disamb. question out of ' + str(int(total)))
    ax1.bar(x, y_values)
    plt.xticks(x, files, rotation='vertical')

    y_values = [sum([v for k, v in json_data[key].iteritems() if 'c' not in k]) / total for key in files]
    print y_values

    ax2 = fig.add_subplot(122)
    ax2.title.set_text('Avg. # of interactions')
    ax2.bar(x, y_values)
    plt.xticks(x, files, rotation='vertical')

    print "diff"
    for item in set([key for __name in files for key in json_data[__name].keys()]):
        try:
            if len(set([json_data[file_name][item] for file_name in files])) > 1:
                # print item, [json_data[file_name][item] for file_name in files]
                pass
        except:
            print item

    plt.show()
