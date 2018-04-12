class UniqueList(list):
    def __init__(self, *args):
        super(UniqueList, self).__init__(*args)

    def addIfNotExists(self, x):
        for item in self:
            if item == x:
                return False
        self.append(x)
        return True
