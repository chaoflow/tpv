class References(object):
    def __init__(self, ids=None, source=None):
        self.ids = ids
        self.source = source

    def __iter__(self):
        return self.iterkeys()

    def iterkeys(self):
        return (id for id in self.ids)

    def iteritems(self):
        return ((id, self.source[id]) for id in self.ids)

    def itervalues(self):
        return (v for k, v in self.iteritems())

    def items(self):
        return self.iteritems()

    def keys(self):
        return self.iterkeys()

    def values(self):
        return self.itervalues()
