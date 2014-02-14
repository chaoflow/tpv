from metachao import aspect
from metachao.aspect import Aspect

## set operations on dicttrees
#
# leading idea: set operations like union, intersection, difference
# and symmetric difference can be applied on two or more dicttrees
# to achieve functionalities like fallback and merge and probably
# more.
#
# there are three different approaches to apply a set operation on
# dicttrees regarding whether one considers the values the keys or the
# pairs of them as the set to be operated on. we call those different
# approaches layers and thus, define the keys, the values and the
# items layer respectively.
#
# For each layer the resulting effect on one recursion depth, will be
# shown in the following form (pseudo code), where the 'op' infix
# represents one of the four set operators:
#
# 1. keys
# { key: A.get(key, B.get(key))
#   for key in ( set(A.keys()) op set(B.keys()) )
#   if A.get(key, B.get(key))) }
#
# 2. values
# { key: ( set(A.get(key, [])) op set(B.get(key, [])) )
#   for key in A.keys()
#   if ( set(A.get(key, [])) op set(B.get(key, [])) ) }
#
# 3. items
# { key: ( set(A.get(key, [])) op set(B.get(key, [])) )
#   for key in ( set(A.keys()) op set(B.keys()) )
#   if ( set(A.get(key, [])) op set(B.get(key, [])) ) }
#
# single values are taken as one item sets. and after the operation
# one items sets are again stored as simple values. if the value to a
# key ends up empty, the key is removed from the dictionary
# (as guaranteed by the if clause in the pseudo code).

# just before the aspect corresponding to each layer we show examples
# of applying the aspect to the following two dicttrees. (reproduced
# just before every example)
#


## keys layer
##
#
# A = {"a" : "A1",
#      "b": { "b1": "B1", "b2": "B2", "b3": "B3" },
#      "c": [ "C1", "C2" ],
#      "d": { "d1": "D1" }}
#
# B = {"a" : "A2",
#      "b": { "b1": "B1", "b2": "Bx", "b4": "B4" },
#      "c": [ "C1", "C3" ],
#      "e": "E1" }
#
## union
# set_oper_dicttree_keys(A, on=B, op="union")
# = {"a": "A1",
#    "b": { "b1": "B1", "b2": "B2", "b3": "B3", "b4": "B4" },
#    "c": [ "C1", "C2" ],
#    "d": { "d1": "D1" },
#    "e": "E1" }
# =: fallback(A, on=B)
#
## intersection
# set_oper_dicttree_keys(A, on=B, op="intersection")
# = {"a": "A1",
#    "b": { "b1": "B1", "b2": "B2" },
#    "c": [ "C1", "C2" ]}
#
## difference
# set_oper_dicttree_keys(A, on=B, op="difference")
# = {"d": { "d1": "D1" }}
# =: filter_out(A, on="B")
#
## symmetric_difference (XOR)
# set_oper_dicttree_keys(A, on=B, op="symmetric_difference")
# = {"d": { "d1": "D1" },
#    "e": "E1" }

class set_oper_dicttree_keys(Aspect):
    # the second dicttree is passed in as on
    on = aspect.config(on=None)
    # op is one of ("union", "intersection", "difference", "symmetric_difference")
    op = aspect.config(op="union")

    @aspect.plumb
    def __getitem__(_next, self, key):
        # whether keys appear is only handled by keys() itself
        if key not in self.keys():
            raise KeyError(key)

        try:
            val_a = _next(key)

            if isinstance(val_a, dict) \
               and key in self.on:
                if isinstance(self.on[key], dict):
                    # values from A and B are branches, thus return
                    # the next recursion level
                    return set_oper_dicttree_keys(val_a, on=self.on[key], op=self.op)
                else:
                    # value from A is a branch and B is a leaf, not coverable
                    raise TypeError("Element for %s is not of type dictionary" % key)
            else:
                # Under the key, A has just a value
                # or (A has a branch and B hasn't anything)
                return val_a
        except KeyError:
            # if the key is not in A,
            pass

        # return the value from B, or raise KeyError
        return self.on[key]

    def iterkeys(self):
        # generator doesn't make sense, we need the full list for set
        # operations
        return iter(self.keys())

    @aspect.plumb
    def keys(_next, self):
        '''Returns a list of keys resulting from the set operation op on the
keys-lists of the two dictionaries'''
        keys_a = set(_next())
        keys_b = set(self.on.keys())
        return list(getattr(keys_a, self.op)(keys_b))


def ensure_set(x):
    '''Return any list, tuple or scalar value as/within a set'''
    if isinstance(x, tuple):
        # tuple
        return set(x)

    try:
        # scalar values need to be tuple'd
        return set((x,))
    except TypeError:
        # list fails the above, with
        # TypeError: unhashable type: 'list'
        return set(x)


## values layer
##
#
# A = {"a" : "A1",
#      "b": { "b1": "B1", "b2": "B2", "b3": "B3" },
#      "c": [ "C1", "C2" ],
#      "d": { "d1": "D1" }}
#
# B = {"a" : "A2",
#      "b": { "b1": "B1", "b2": "Bx", "b4": "B4" },
#      "c": [ "C1", "C3" ],
#      "e": "E1" }
#
## union
# set_oper_dicttree_values(A, on=B, op="union")
# = {"a": ["A1", "A2"],
#    "b": { "b1": "B1", "b2": ["B2", "Bx"], "b3": "B3" },
#    "c": [ "C1", "C2", "C3" ],
#    "d": { "d1": "D1" }}
#
## intersection
# set_oper_dicttree_values(A, on=B, op="intersection")
# = {"b": { "b1": "B1" },
#    "c": "C1"}
#
## difference
# set_oper_dicttree_values(A, on=B, op="difference")
# = {"a": "A1",
#    "b": { "b2": "B2", "b3": "B3" },
#    "c": "C2",
#    "d": { "d1": "D1" }}
#
## symmetric_difference
# set_oper_dicttree_values(A, on=B, op="symmetric_difference")
# = {"a": ["A1", "A2"],
#    "b": { "b2": ["B2", "Bx"], "b3": "B3" },
#    "c": [ "C2", "C3" ],
#    "d": { "d1": "D1" }}

class set_oper_dicttree_values(Aspect):
    # the second dicttree is passed in as on
    on = aspect.config(on=None)
    # op is one of ("union", "intersection", "difference", "symmetric_difference")
    op = aspect.config(op="union")

    @aspect.plumb
    def __getitem__(_next, self, key):
        # get the values from the two dictionaries
        # if the key is not in A, it's not meant to be in the result,
        # thus allow A to raise KeyError, but not B
        val_a = _next(key)
        val_b = self.on.get(key, [])

        # check for branches
        if isinstance(val_a, dict):
            if isinstance(val_b, dict):
                # both are branches, do the recursion
                return set_oper_dicttree_values(val_a, on=val_b, op=self.op)
            elif key not in self.on:
                # A is branch, B is empty
                if self.op == 'intersection':
                    # for an intersection, key has to exist in B
                    raise KeyError(key)
                else:
                    # for union, (symmetric_)difference the branch
                    # from A remains
                    return val_a
            else:
                # A is branch, B has a leaf: misaligned case
                raise TypeError("Element for %s is not of type dictionary" % key)

        # apply the set operation on the values
        ret = getattr(ensure_set(val_a), self.op)(ensure_set(val_b))

        if len(ret) == 0:
            # nothing remains as value, thus KeyError
            raise KeyError(key)
        elif len(ret) == 1:
            # just one value remains, cast to scalar value
            return ret.pop()
        else:
            # convert set to list
            return list(ret)

    def __contains__(self, key):
        # as we don't want to list a key, for which no value remains
        # after the set operation, we have to use __getitem__
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def keys(self):
        return list(self.iterkeys())

    @aspect.plumb
    def iterkeys(_next, self):
        # use the __contains__ function to filter available keys
        return (key for key in _next() if key in self)


## items layer
##
#
# A = {"a" : "A1",
#      "b": { "b1": "B1", "b2": "B2", "b3": "B3" },
#      "c": [ "C1", "C2" ],
#      "d": { "d1": "D1" }}
#
# B = {"a" : "A2",
#      "b": { "b1": "B1", "b2": "Bx", "b4": "B4" },
#      "c": [ "C1", "C3" ],
#      "e": "E1" }
#
## union
# set_oper_dicttree_items(A, on=B, op="union")
# = {"a": ["A1", "A2"],
#    "b": { "b1": "B1", "b2": ["B2", "Bx"], "b3": "B3", "b4": "B4" },
#    "c": [ "C1", "C2", "C3" ],
#    "d": { "d1": "D1" },
#    "e": "E1"}
# =: merge(A, on=B)
#
## intersection
# set_oper_dicttree_items(A, on=B, op="intersection")
# = {"b": { "b1": "B1" },
#    "c": "C1"}
# =: sameitems(A, on=B) ( = match(A, on=B) )
#
## difference
# set_oper_dicttree_items(A, on=B, op="difference")
# = {"d": { "d1": "D1" }}
#
## symmetric_difference
# set_oper_dicttree_items(A, on=B, op="symmetric_difference")
# = {"d": { "d1": "D1" },
#    "e": "E1"}

class set_oper_dicttree_items(Aspect):
    # the second dicttree is passed in as on
    on = aspect.config(on=None)
    # op is one of ("union", "intersection", "difference", "symmetric_difference")
    op = aspect.config(op="union")

    @aspect.plumb
    def __getitem__(_next, self, key, thorough=True):
        # check, whether the key remains after the set operation on
        # the keys. but don't do this, when called from iterkeys, else
        # we land in infinite recursion.
        if thorough and key not in self.keys(thorough=False):
            raise KeyError(key)

        # values for A and B with fallbacks
        try:
            val_a = _next(key)
            key_is_in_a = True
        except KeyError:
            # provide an empty fallback for value from A and record
            # we had to, to cover the case where B is a branch and A
            # is empty.
            val_a = []
            key_is_in_a = False

        val_b = self.on.get(key, [])

        # check for branches
        if isinstance(val_a, dict):
            if isinstance(val_b, dict):
                # both are branches, do the recursion
                return set_oper_dicttree_items(val_a, on=val_b, op=self.op)
            elif key not in self.on:
                # we know, that self.op != 'intersection' at this
                # point (because then key is not in self.keys()). for
                # all other operations, it's fine to return the branch
                # from A
                return val_a
            else:
                # A is branch, B is leaf: misaligned case
                raise TypeError("Element for %s is not of type dictionary" % key)
        elif isinstance(val_b, dict):
            if not key_is_in_a:
                # B is a branch, A is empty
                # as the key was accepted, by the iterkeys() function,
                # self.op is in ("union", "symmetric_difference") and
                # thus return the sole branch from B
                return val_b
            else:
                # B is a branch, A is leaf: misaligned case
                raise TypeError("Element for %s is not of type dictionary" % key)

        # set operations on values
        ret = getattr(ensure_set(val_a), self.op)(ensure_set(val_b))

        if len(ret) == 0:
            # nothing remains as value, thus KeyError
            raise KeyError(key)
        elif len(ret) == 1:
            # just one value remains, cast to scalar value
            return ret.pop()
        else:
            # convert set to list
            return list(ret)

    def __contains__(self, key, thorough=True):
        # check, whether any values remain after the set
        # operations. For thorough==True, check set operations for
        # values and keys. For thorough==False, check only set
        # operation on values.
        try:
            self.__getitem__(key, thorough=thorough)
            return True
        except KeyError:
            return False

    def keys(self, thorough=True):
        return list(self.iterkeys(thorough))

    @aspect.plumb
    def iterkeys(_next, self, thorough=True):
        # 1. apply the set operation on the two key lists
        keys_a = set(_next())
        keys_b = set(self.on.keys())
        keys = getattr(keys_a, self.op)(keys_b)

        # thorough is used to break the dependency cycle between
        # __getitem__ and keys.
        if not thorough:
            # if called from __getitem__, we don't want to recurse
            # into __getitem again
            return keys
        else:
            # 2. a key might still not be in the keys of the result,
            # if the set operation on the values turns out empty
            return (key for key in keys
                    if self.__contains__(key, thorough=False))


# return for each key values from B, if it is not found in A
fallback = set_oper_dicttree_keys(op="union")

# merge keys from A and B. if the key shows up in both, merge the
# values. if it's just in one, take it.
merge = set_oper_dicttree_items(op="union")

# removes all the keys from A, which are in B
filter_out = set_oper_dicttree_keys(op="difference")

# set_oper_dicttree_values(op="difference") might also make sense


class cache(Aspect):
    # allow to supply a dictionary to be used as the cach'ing object
    # initialised as an empty dictionary by the constructor if None.
    cache = aspect.config(cache=None)

    # class of which the instances are to be cached
    node_class = aspect.config(node_class=dict)

    def _get_cache(self, node):
        '''Returns a cache object for a given node'''
        return getattr(node, "cache_class", self.cache.__class__
                       if self.cache is not None else dict)()

    def _wrap_child(self, child):
        return cache(child, cache=self._get_cache(child))

    @aspect.plumb
    def __init__(_next, self, *args, **kwargs):
        if self.cache is None:
            self.cache = self._get_cache(self)

        # if not None, contains the whole list of keys (so that
        # repetitive calls to keys() are cached)
        self.cache_keys = None

        # marks, whether self.cache contains the whole dictionary
        self.cache_complete = False

        _next(*args, **kwargs)

    @aspect.plumb
    def __getitem__(_next, self, key):
        # try first in cache
        try:
            return self.cache[key]
        except KeyError:
            pass

        # else from the source
        ret = _next(key)

        if isinstance(ret, self.node_class):
            # branch case, do the recursion
            ret = self._wrap_child(ret)

        # commit value to cache
        self.cache[key] = ret

        return ret

    @aspect.plumb
    def __setitem__(_next, self, key, val):
        # hand through
        _next(key, val)
        # update cache
        self.cache[key] = val
        # keep cache_keys up-to-date
        if self.cache_keys is not None and key not in self.cache_keys:
            self.cache_keys.append(key)

    @aspect.plumb
    def update(_next, self, E, **F):
        # hand through
        _next(E, **F)
        # update cache
        self.cache.update(E, **F)

        if self.cache_keys is not None:
            keys = set()
            if E:
                if hasattr(E, "keys"):
                    keys.update(E.keys())
                else:
                    keys.update(v for k, v in E)

            keys.update(F.keys())

            self.cache_keys += list(keys.difference(self.cache_keys))

    @aspect.plumb
    def __iter__(_next, self):
        if self.cache_keys is None:
            # start assembling a candidate for self.cache_keys
            tmp_cache_keys = []

            # iterate over keys from source
            for key in _next():
                tmp_cache_keys.append(key)
                yield key

            # StopIteration received, thus tmp_cache_keys is complete
            self.cache_keys = tmp_cache_keys
        else:
            # cache_keys is complete, iterate it
            for key in iter(self.cache_keys):
                yield key

    iterkeys = __iter__

    def itervalues(self):
        # implemented based on iteritems to be able to fill the cache
        for key, val in self.iteritems():
            yield val

    @aspect.plumb
    def iteritems(_next, self):
        if self.cache_complete:
            # the cache is complete return directly from it.

            # mixing iterators and return fails, thus as a shallow
            # generator
            for x in self.cache.iteritems():
                yield x
        else:
            for key, val in _next():
                if isinstance(val, self.node_class):
                    # branch case, do the recursion
                    val = self._wrap_child(val)

                # update in cache
                self.cache[key] = val
                # pass out, as generator
                yield (key, val)

            # StopIteration was reached, the cache is now complete
            self.cache_complete = True
            # cache_keys are thus fully generated
            self.cache_keys = self.cache.keys()

    # the non-generator functions, are overwritten to use the
    # generator ones (they use the cache)
    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    # provide a function to empty the cache, when one uses
    # side-channels to change the source
    def clear_cache(self):
        self.cache = self._get_cache(self)
        self.cache_complete = False
        self.cache_keys = []
