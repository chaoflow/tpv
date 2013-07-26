from __future__ import absolute_import

from metachao.classnode import classnode

from ..ordereddict import OrderedDict
from ..testing import unittest

from .. import aspects


class TestCase(unittest.TestCase):
    def setUp(self):
        class Base(OrderedDict):
            __metaclass__ = classnode

        class Root(Base):
            pass

        class A(Base):
            pass

        class B(Base):
            pass

        Root['a'] = A
        Root['b'] = B
        A['b'] = B
        B['a'] = A

        self.Root = Root
        self.A = A
        self.B = B

    def test_seed(self):
        Root = aspects.seed_tree(self.Root, seed_factories=self.Root)
        root = Root()
        self.assertTrue(isinstance(root, Root))
        self.assertTrue(isinstance(root['a'], self.A))
        self.assertTrue(isinstance(root['b'], self.B))
        self.assertTrue(isinstance(root['a']['b'], self.B))
        self.assertTrue(isinstance(root['b']['a'], self.A))
