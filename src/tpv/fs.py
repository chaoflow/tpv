import os


class Node(object):
    def __init__(self, path=None):
        if path is not None:
            self.abspath = os.path.abspath(path)


class File(Node):
    pass


class Link(Node):
    pass


class Directory(Node):
    def childpath(self, key):
        return os.path.sep.join([self.abspath, key])

    def __iter__(self):
        return iter(sorted(os.listdir(self.abspath)))

    def keys(self):
        return list(self)

    def __getitem__(self, key):
        childpath = self.childpath(key)

        # does the path exist?
        if not os.path.exists(childpath):
            raise KeyError(key)

        # determine factory for child
        Child = factory(childpath)
        return Child(childpath)


def factory(path):
    if os.path.islink(path):
        Child = Link
    elif os.path.isdir(path):
        Child = Directory
    elif os.path.isfile(path):
        Child = File
    else:
        Child = Node
    return Child

HOME = Directory(path=os.environ['HOME'])
