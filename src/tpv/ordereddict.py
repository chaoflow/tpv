from __future__ import absolute_import

try:
    from collections import OrderedDict as _OrderedDict
except ImportError:
    from ordereddict import OrderedDict as _OrderedDict

from . import aspects


@aspects.set_children_on_init
@aspects.getattr_children
class Node(_OrderedDict):
    pass
