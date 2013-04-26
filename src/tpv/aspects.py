import metachao
from metachao import aspect
from metachao.aspect import Aspect


class getattr_children(Aspect):
    def __getattr__(self, name):
        """Blend in children as attributes

        Children can be accessed via getattr, except if aliased by a
        real attribute.
        """
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)


class set_children_on_init(Aspect):
    """Set children during init
    """
    @aspect.plumb
    def __init__(_next, self, children=None, **kw):
        _next(self, **kw)
        if children is not None:
            self.update(children)


class configure(Aspect):
    """Provide configuration

    Instantiates a model's classes on demand, supplying them config.

    This creates the read only part of a model.

    """
    config = aspect.aspectkw(config=None)

    # XXX: needed for now as prototyping does not work as expected yet
    # XXX: might work also via inheritance
    def __getattr__(self, name):
        """Blend in children as attributes

        Children can be accessed via getattr, except if aliased by a
        real attribute.
        """
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    @aspect.plumb
    def __getitem__(_next, self, key):
        node = _next(key)
        config = (self.config or dict()).get(key, dict())
        if metachao.utils.isclass(node):
            # XXX: this destroys order
            node = node(**config)
        else:
            node = configure(node, config=config)
        return node

    def values(self):
        for k in self.keys():
            yield self[k]


class keys(Aspect):
    def keys(self):
        return list(self)


class values(Aspect):
    def values(self):
        return list(self.itervalues())


class items(Aspect):
    def items(self):
        return list(self.iteritems())
