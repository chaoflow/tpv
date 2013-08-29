from itertools import izip

from metachao import aspect
from metachao.aspect import Aspect

## set operations on dicttrees


# keys layer
class set_oper_dicttree_keys(Aspect):
    on = aspect.config(on=None)
    op = aspect.config(op="union")

    @aspect.plumb
    def __getitem__(_next, self, key):
        if key not in self.keys():
            raise KeyError(key)

        try:
            val_a = _next(key)
            if isinstance(val_a, dict) \
               and key in self.on:
                if isinstance(self.on[key], dict):
                    return set_oper_dicttree_keys(val_a, on=self.on[key], op=self.op)
                else:
                    raise TypeError("Element for %s is not of type dictionary" % key)
            else:
                return val_a
        except KeyError:
            pass

        return self.on[key]

    def iterkeys(self):
        return iter(self.keys())

    @aspect.plumb
    def keys(_next, self):
        keys_a = set(_next())
        keys_b = set(self.on.keys())
        return list(getattr(keys_a, self.op)(keys_b))


def ensure_set(x):
    if isinstance(x, tuple):
        return set(x)
    else:
        try:
            return set((x,))
        except TypeError:
            return set(x)


# values layer
class set_oper_dicttree_values(Aspect):
    on = aspect.config(on=None)
    op = aspect.config(op="union")

    @aspect.plumb
    def __getitem__(_next, self, key):
        val_a = _next(key)
        val_b = self.on.get(key, [])

        if isinstance(val_a, dict):
            if isinstance(val_b, dict):
                return set_oper_dicttree_values(val_a, on=val_b, op=self.op)
            elif key not in self.on:
                if self.op == 'intersection':
                    raise KeyError(key)
                else:
                    return val_a
            else:
                raise TypeError("Element for %s is not of type dictionary" % key)

        ret = getattr(ensure_set(val_a), self.op)(ensure_set(val_b))

        if len(ret) == 0:
            raise KeyError(key)
        elif len(ret) == 1:
            return ret.pop()
        else:
            return list(ret)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def keys(self):
        return list(self.iterkeys())

    @aspect.plumb
    def iterkeys(_next, self):
        return (key for key in _next() if key in self)


# items layer
class set_oper_dicttree_items(Aspect):
    on = aspect.config(on=None)
    op = aspect.config(op="union")

    @aspect.plumb
    def __getitem__(_next, self, key, thorough=True):
        if thorough and key not in self.keys(thorough=False):
            raise KeyError(key)

        try:
            val_a = _next(key)
            key_is_in_a = True
        except KeyError:
            val_a = []
            key_is_in_a = False

        val_b = self.on.get(key, [])

        if isinstance(val_a, dict):
            if isinstance(val_b, dict):
                return set_oper_dicttree_items(val_a, on=val_b, op=self.op)
            elif key not in self.on:
                # we know, that self.op != 'intersection' at this point
                return val_a
            else:
                raise TypeError("Element for %s is not of type dictionary" % key)
        elif isinstance(val_b, dict):
            if not key_is_in_a:
                if self.op == 'difference':
                    raise KeyError(key)
                else:
                    return val_b
            else:
                raise TypeError("Element for %s is not of type dictionary" % key)

        ret = getattr(ensure_set(val_a), self.op)(ensure_set(val_b))

        if len(ret) == 0:
            raise KeyError(key)
        elif len(ret) == 1:
            return ret.pop()
        else:
            return list(ret)

    def __contains__(self, key, thorough=True):
        try:
            self.__getitem__(key, thorough=thorough)
            return True
        except KeyError:
            return False

    def keys(self, thorough=True):
        return list(self.iterkeys(thorough))

    @aspect.plumb
    def iterkeys(_next, self, thorough=True):
        keys_a = set(_next())
        keys_b = set(self.on.keys())
        keys = getattr(keys_a, self.op)(keys_b)

        if not thorough:
            return keys
        else:
            return (key for key in keys
                    if self.__contains__(key, thorough=False))

fallback = set_oper_dicttree_keys(op="union")

merge = set_oper_dicttree_items(op="union")


class cache(Aspect):
    cache = aspect.config(cache=None)

    @aspect.plumb
    def __init__(_next, self):
        if self.cache is None:
            self.cache = dict()

        self.cache_keys = None
        self.cache_complete = False

        _next()

    @aspect.plumb
    def __getitem__(_next, self, key):
        try:
            return self.cache[key]
        except KeyError:
            pass

        ret = _next(key)
        if isinstance(ret, dict):
            ret = cache(ret)
            # XXX, cache object must be configurable
            # also for children

        self.cache[key] = ret
        return ret

    @aspect.plumb
    def __setitem__(_next, self, key, val):
        _next(key, val)
        self.cache[key] = val
        if self.cache_keys is not None and key not in self.cache_keys:
            self.cache_keys.append(key)

    @aspect.plumb
    def __iter__(_next, self):
        if self.cache_keys is None:
            tmp_cache_keys = []

            for key in _next():
                tmp_cache_keys.append(key)
                yield key

            self.cache_keys = tmp_cache_keys
        else:
            for key in iter(self.cache_keys):
                yield key

    iterkeys = __iter__

    # def itervalues(self):
    #     # XXX should possibly be implemented based on plumbing for
    #     # speed reasons
    #     for key in iter(self):
    #         yield self[key]

    def itervalues(self):
        for key, val in self.iteritems():
            yield val

    # def iteritems(self):
    #     return izip(self.iterkeys(), self.itervalues())

    @aspect.plumb
    def iteritems(_next, self):
        if self.cache_complete == False:
            for key, val in _next():
                if isinstance(val, dict):
                    val = cache(val)
                    # XXX, cache object must be configurable
                    # also for children

                self.cache[key] = val
                yield (key, val)

            self.cache_complete = True
            self.cache_keys = self.cache.keys()
        else:
            for x in self.cache.iteritems():
                yield x

            # mixing iterators and return fails?!
            # return self.cache.iteritems()

    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def clear_cache(self):
        self.cache = dict()
        self.cache_complete = False
        self.cache_keys = []
