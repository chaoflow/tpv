from ..ordereddict import Node, OrderedDict
from ..testing import unittest

from .. import generic
from ..generic import ensure_set

A = OrderedDict({"a": ["foo", "bar"], "b": OrderedDict({"b1": "A2", "b2": "A3"}), "d": "A4", "f": "A5"})
B = OrderedDict({"a": ["bar", "baz"], "b": OrderedDict({"b1": "B2", "b3": "B3"}), "d": "A4", "e": "B4"})

class TestEnsureSet(unittest.TestCase):
    def test_ensureset(self):
        self.assertEqual(ensure_set("string"), set(("string",)))
        self.assertEqual(ensure_set(1), set((1,)))
        self.assertEqual(ensure_set(["a", "b"]), set(("a", "b")))
        self.assertEqual(ensure_set(("a", "b")), set(("a", "b")))
        self.assertEqual(ensure_set(["string"]), set(("string",)))
        self.assertEqual(ensure_set(set(("a",))), set(("a",)))

class TestSetOperDictTreeKeys(unittest.TestCase):

    def test_intersection(self):
        C = generic.set_oper_dicttree_keys(A, on=B, op="intersection")
        self.assertEqual(set(C.keys()), set(("a", "b", "d")))
        self.assertEqual(C["a"], ["foo", "bar"])
        self.assertEqual(C["d"], "A4")

        self.assertEqual(set(C["b"].keys()), set(("b1",)))
        self.assertRaises(KeyError, lambda: C["b"]["b2"])
        self.assertEqual(C["b"]["b1"], "A2")

    def test_union(self):
        C = generic.set_oper_dicttree_keys(A, on=B, op="union")
        self.assertEqual(C["a"], ["foo", "bar"])
        self.assertEqual(C["e"], "B4")
        self.assertEqual(set(C.keys()), set(("a", "b", "d", "e", "f")))

        self.assertEqual(set(C["b"].keys()), set(("b1","b2","b3")))
        self.assertEqual(C["b"]["b1"], "A2")
        self.assertEqual(C["b"]["b2"], "A3")
        self.assertEqual(C["b"]["b3"], "B3")


class TestSetOperDictTreeValues(unittest.TestCase):

    def test_intersection(self):
        C = generic.set_oper_dicttree_values(A, on=B, op="intersection")
        self.assertEqual(set(C.keys()), set(("a", "b", "d")))
        self.assertEqual(C["a"], "bar")
        # import ipdb; ipdb.set_trace()
        self.assertEqual(C["d"], "A4")

        self.assertEqual(set(C["b"].keys()), set())
        self.assertRaises(KeyError, lambda: C["b"]["b1"])

    def test_union(self):
        C = generic.set_oper_dicttree_values(A, on=B, op="union")

        self.assertEqual(set(C.keys()), set(("a", "b", "d", "f")))
        self.assertTrue(isinstance(C["a"], list))
        self.assertEqual(set(C["a"]), set(["foo", "bar", "baz"]))
        self.assertEqual(C["d"], "A4")
        self.assertEqual(C["f"], "A5")

        self.assertEqual(set(C["b"].keys()), set(("b1","b2")))
        self.assertEqual(C["b"]["b1"], ["A2", "B2"])
        self.assertEqual(C["b"]["b2"], "A3")

class TestSetOperDictTreeItems(unittest.TestCase):

    def test_intersection(self):
        C = generic.set_oper_dicttree_items(A, on=B, op="intersection")
        self.assertEqual(set(C.keys()), set(("a", "b", "d")))
        self.assertEqual(C["a"], "bar")
        # import ipdb; ipdb.set_trace()
        self.assertEqual(C["d"], "A4")

        self.assertEqual(set(C["b"].keys()), set())
        self.assertRaises(KeyError, lambda: C["b"]["b1"])

    def test_union(self):
        C = generic.set_oper_dicttree_items(A, on=B, op="union")

        self.assertEqual(set(C.keys()), set(("a", "b", "d", "e", "f")))
        self.assertTrue(isinstance(C["a"], list))
        self.assertEqual(set(C["a"]), set(["foo", "bar", "baz"]))
        self.assertEqual(C["d"], "A4")
        self.assertEqual(C["e"], "B4")
        self.assertEqual(C["f"], "A5")

        self.assertEqual(set(C["b"].keys()), set(("b1","b2","b3")))
        self.assertEqual(C["b"]["b1"], ["A2", "B2"])
        self.assertEqual(C["b"]["b2"], "A3")
        self.assertEqual(C["b"]["b3"], "B3")


class TestFallback(unittest.TestCase):

    def test_union(self):
        C = generic.fallback(A, on=B)
        self.assertEqual(C["a"], ["foo", "bar"])
        self.assertEqual(C["e"], "B4")
        self.assertEqual(set(C.keys()), set(("a", "b", "d", "e", "f")))

        self.assertEqual(set(C["b"].keys()), set(("b1","b2","b3")))
        self.assertEqual(C["b"]["b1"], "A2")
        self.assertEqual(C["b"]["b2"], "A3")
        self.assertEqual(C["b"]["b3"], "B3")


class TestMerge(unittest.TestCase):

    def test_union(self):
        C = generic.merge(A, on=B)

        self.assertEqual(set(C.keys()), set(("a", "b", "d", "e", "f")))
        self.assertTrue(isinstance(C["a"], list))
        self.assertEqual(set(C["a"]), set(["foo", "bar", "baz"]))
        self.assertEqual(C["d"], "A4")
        self.assertEqual(C["e"], "B4")
        self.assertEqual(C["f"], "A5")

        self.assertEqual(set(C["b"].keys()), set(("b1","b2","b3")))
        self.assertEqual(C["b"]["b1"], ["A2", "B2"])
        self.assertEqual(C["b"]["b2"], "A3")
        self.assertEqual(C["b"]["b3"], "B3")


class TestCache(unittest.TestCase):

    def setUp(self):
        self.A = OrderedDict({"a": ["foo", "bar"], "b": OrderedDict({"b1": "A2", "b2": "A3"}), "d": "A4", "f": "A5"})

    def test_getitem(self):
        C = generic.cache(self.A)

        self.assertEqual(C["a"], self.A["a"])
        self.A["a"] = "overwrite"
        self.assertNotEqual(C["a"], "overwrite")
        self.assertEqual(C["b"], self.A["b"])
        self.assertRaises(KeyError, lambda: C["c"])

    def test_setitem(self):
        C = generic.cache(self.A)

        orig = C['b']
        C['b'] = 'overwrite'

        self.assertEqual(self.A['b'], 'overwrite')
        self.assertEqual(C['b'], 'overwrite')

    def test_update(self):
        C = generic.cache(self.A)

        # put keys into cache
        C.keys()

        C.update({'b': 'new_b'}, d='new_d', e='new_e')

        self.assertEqual(self.A['b'], 'new_b')
        self.assertEqual(C['b'], 'new_b')

        self.assertEqual(self.A['d'], 'new_d')
        self.assertEqual(C['d'], 'new_d')

        self.assertTrue('e' in C.cache_keys)
        self.assertTrue('e' in C.keys())

    def test_getitem_on_children(self):
        C = generic.cache(self.A)
        Ab = self.A["b"]
        Cb = C["b"]

        self.assertEqual(Cb["b1"], Ab["b1"])
        Ab["b1"] = "overwrite"
        self.assertNotEqual(Cb["b1"], "overwrite")
        self.assertEqual(Cb["b2"], Ab["b2"])
        self.assertRaises(KeyError, lambda: Cb["c"])
