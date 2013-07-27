from __future__ import absolute_import

import tpv.pkg_resources

from metachao.classnode import ClassNode
from tpv.testing import unittest


class Root(ClassNode):
    pass


class A(ClassNode):
    pass


class B(ClassNode):
    pass


class AA(ClassNode):
    pass


class AB(ClassNode):
    pass


class TestCase(unittest.TestCase):
    def test_tree_from_entry_points(self):
        tpv.pkg_resources.load_entry_points('tpv.tests.eps', Root)
        self.assertEqual(Root['a'], A)
        self.assertEqual(Root['a']['a'], AA)
        self.assertEqual(Root['a']['b'], AB)
        self.assertEqual(Root['b'], B)
