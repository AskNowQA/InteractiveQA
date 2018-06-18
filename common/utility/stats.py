from common.utility.utils import Utils
import json, os


class Stats(dict):
    def __init__(self, *args):
        # dict.__init__(self, args)
        super(dict, self).__init__(*args)

    def __getitem__(self, key):
        if key not in self:
            return 0
        return dict.__getitem__(self, key)

    def inc(self, key, value=1):
        if key not in self:
            self[key] = 0
        self[key] += value

    @staticmethod
    def load(file_path):
        if os.path.exists(file_path):
            with open(file_path) as data_file:
                data = json.load(data_file)
                output = Stats()
                for item in data:
                    output[item] = data[item]
                return output
        return Stats()

    def save(self, output_file):
        Utils.makedirs(os.path.dirname(output_file))
        with open(output_file, "w") as data_file:
            json.dump(self, data_file, sort_keys=True, indent=4, separators=(',', ': '))

    def __str__(self):
        keys = self.keys()
        keys.sort()
        return " ".join([key + ":" + str(self[key]) for key in keys])
