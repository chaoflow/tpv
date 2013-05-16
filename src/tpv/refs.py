from __future__ import absolute_import

import ldap


class References(object):
    def __init__(self, ldaplist=None, ids=None, source=None):
        self.ldaplist = ldaplist
        self.ids = ids
        self.source = source

    def __iter__(self):
        return self.iterkeys()

    def __contains__(self, id):
        return id in self.ids

    def iterkeys(self):
        return (id for id in self.ids)

    def iteritems(self):
        return ((id, self.source[id]) for id in self.ids)

    def itervalues(self):
        return (v for k, v in self.iteritems())

    def items(self):
        return self.iteritems()

    def keys(self):
        return self.iterkeys()

    def remove(self, id):
        """remove id from referenced items
        """
        try:
            self.ldaplist.remove(id)
        except ldap.NO_SUCH_ATTRIBUTE:
            pass

    def update(self, id):
        """add id to the referenced items
        """
        try:
            self.ldaplist.append(id)
        except ldap.TYPE_OR_VALUE_EXISTS:
            pass

    def values(self):
        return self.itervalues()
