from __future__ import absolute_import

import metachao.utils
import pkg_resources

from metachao import aspect


class children_from_entry_points(aspect.Aspect):
    _entry_point_group = aspect.config(entry_point_group=None)

    @aspect.plumb
    def __init__(_next, self, **kw):
        _next(**kw)
        eps = sorted(pkg_resources.iter_entry_points(self._entry_point_group),
                     key=lambda x: x.name)
        for ep in eps:
            path = ep.name.split('/')
            name = path.pop()
            parent = self
            while path:
                parent = parent[path.pop(0)]
            node = ep.load()
            if metachao.utils.isclass(node):
                node = node()
            parent[name] = node
