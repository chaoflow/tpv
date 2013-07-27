from __future__ import absolute_import

import tpv.pkg_resources

from metachao import classtree
from tpv.testing import unittest


class Root(classtree.Node):
    pass


class A(classtree.Node):
    pass


class B(classtree.Node):
    pass


class AA(classtree.Node):
    pass


class AB(classtree.Node):
    pass


class TestCase(unittest.TestCase):
    def test_tree_from_entry_points(self):
        tpv.pkg_resources.load_entry_points('tpv.tests.eps', Root)
        self.assertEqual(Root['a'], A)
        self.assertEqual(Root['a']['a'], AA)
        self.assertEqual(Root['a']['b'], AB)
        self.assertEqual(Root['b'], B)
