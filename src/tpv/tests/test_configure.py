from ..ordereddict import Node
from ..testing import unittest

from .. import aspects


CONFIG = Node(children=(
    ('a', Node(children=(
        ('aa', 11),
        ('ab', 12),
    ))),
    ('b', Node(children=(
        ('ba', Node(children=(
            ('baa', 211),
        ))),
        ('bb', 22),
    ))),
    # XXX: should raise a warning: unused configuration
    ('d', Node(children=(
        ('da', 41),
    ))),
))


MODEL = Node(children=(
    ('a', Node),
    ('b', Node),
    ('c', Node),
))


class TestCase(unittest.TestCase):
    app = aspects.configure(MODEL, config=CONFIG)

    def runTest(self):
        app = self.app
        self.assertEqual(list(app.keys()), ['a', 'b', 'c'])
        self.assertEqual(list(app.a.keys()), ['aa', 'ab'])
        self.assertEqual(app.a.aa, 11)
        self.assertEqual(app.a.ab, 12)
        self.assertEqual(list(app.b.keys()), ['ba', 'bb'])
        self.assertEqual(app.b.ba.baa, 211)
        self.assertEqual(app.b.bb, 22)
