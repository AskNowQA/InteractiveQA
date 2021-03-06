import os
import json


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
            try:
                with open(self.file_path) as data_file:
                    data = json.load(data_file)
                    for item in data:
                        self[item] = data[item]
            except:
                pass

    def save(self):
        with open(self.file_path, "w") as data_file:
            json.dump(self, data_file, sort_keys=True, indent=4, separators=(',', ': '))
