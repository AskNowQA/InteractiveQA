import os
import json
from utils import Utils


class CacheDict(dict):
    def __init__(self, file_path, auto_load=True, *args):
        super(dict, self).__init__(*args)
        self.file_path = file_path
        if auto_load:
            self.load()

    def __setitem__(self, k, v):
        output = super(CacheDict, self).__setitem__(k, v)
        self.save()
        return output

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path) as data_file:
                data = json.load(data_file)
                output = CacheDict()
                for item in data:
                    output[item] = data[item]
                return output
        return CacheDict(self.file_path, False)

    def save(self):
        Utils.makedirs(os.path.dirname(self.file_path))
        with open(self.file_path, "w") as data_file:
            json.dump(self, data_file, sort_keys=True, indent=4, separators=(',', ': '))
