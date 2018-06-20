class UniqueList(list):
    def __init__(self, *args):
        super(UniqueList, self).__init__(*args)

    def add_if_not_exists(self, x):
        for item in self:
            if item == x:
                return item
        self.append(x)
        return x

    def add_or_update(self, x, eq_func, opt_func):
        for idx in range(len(self)):
            item = self[idx]
            if eq_func(item, x):
                self[idx] = opt_func(item, x)
                return self[idx]
        self.append(x)
        return x
