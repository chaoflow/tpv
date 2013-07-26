import metachao
from metachao import aspect
from metachao.aspect import Aspect


class child_aspect(Aspect):
    child_aspect = aspect.aspectkw(child_aspect=None)

    @aspect.plumb
    def __getitem__(_next, self, key):
        child = _next(key)
        if self.child_aspect:
            # XXX: hack
            dn = child.dn
            directory = child.directory
            child = self.child_aspect(child)
            child.dn = dn
            child.directory = directory
        return child

    @aspect.plumb
    def search(_next, self, *args, **kw):
        for node in _next(*args, **kw):
            if self.child_aspect:
                # XXX: hack
                dn = node.dn
                directory = node.directory
                node = self.child_aspect(node)
                node.dn = dn
                node.directory = directory
            yield node


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
    def values(self, **kw):
        return list(self.itervalues(**kw))


class items(Aspect):
    def items(self, **kw):
        return list(self.iteritems(**kw))


class seed_tree(Aspect):
    _seed_factories = aspect.config(None)

    @aspect.plumb
    def __getitem__(_next, self, key):
        try:
            return _next(key)
        except KeyError:
            pass

        factory = self._seed_factories[key]
        factory = seed_tree(factory, seed_factories=factory)
        node = factory()
        self[key] = node
        return node
