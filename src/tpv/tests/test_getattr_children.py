from __future__ import absolute_import

from metachao import aspect
from metachao.aspect import Aspect

from ..ordereddict import Node
from ..testing import unittest

from .. import aspects


class getitem42(Aspect):
    @aspect.plumb
    def __getitem__(_next, self, key):
        if key == 'a':
            return 42
        return _next(key)


ROOT = Node(
    a=1,
    b=Node(
        ba=21,
        bb=22,
    ),
)

ROOT42 = getitem42(Node)()


class TestCase(unittest.TestCase):
    root = ROOT
    root42 = ROOT42

    def test_instance(self):
        root = self.root
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b.ba, 21)
        self.assertEqual(root.b.bb, 22)

    def test_prototyped(self):

        class a(Aspect):
            pass

        root = a(self.root)
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b.ba, 21)
        self.assertEqual(root.b.bb, 22)

    def test_chained_getitem(self):
        root = self.root42
        self.assertEqual(root['a'], 42)
        self.assertEqual(root.a, 42)

    def test_chained_getitem_prototyped(self):
        root = getitem42(self.root)
        # XXX: we don't like this behaviour
        self.assertEqual(root.a, 1)
        # XXX: and the workaround - which does not work
        root = aspects.getattr_children(getitem42(self.root))
        self.assertEqual(root['a'], 42)
        self.assertEqual(root.a, 42)
