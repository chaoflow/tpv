from __future__ import absolute_import

import pkg_resources


def load_entry_points(group, root):
    """Load entry points for group into root
    """
    eps = sorted(pkg_resources.iter_entry_points(group), key=lambda x: x.name)
    for ep in eps:
        path = ep.name.split('/')
        name = path.pop()
        parent = root
        while path:
            parent = parent[path.pop(0)]
        node = ep.load()
        parent[name] = node
