from metachao import aspect
import re


###
#
# Event subscription logic

tpv_subscriber_exact = dict()
tpv_subscriber_regex = dict()

def notify(evtype, evdata):
    '''Fire event `evtype`

Call all functions, who have been subscribed to react to event-type `evtype`.
s
See also `subscribe`.

Usage example:

    tpv.event.notify('user-approved', userdata)
    '''

    # we split the subscriptions into exact ones and regex ones for
    # better performance
    # both will be filled by the same subscribe decorator, see below.

    for (func, extra_args) in tpv_subscriber_exact.get(evtype,[]):
        func(evdata, *extra_args)

    for regex, functions in tpv_subscriber_regex.iteritems():
        if re.match(regex, evtype):
            for func, extra_args in functions:
                func(evtype, evdata, *extra_args)


def subscribe(type=None, extra_args=(), regex=None):
    '''Subscribe a function as an event handler using decorators

Supply either `type`, which has to match the event-type exactly, or
`regex`, which is matched against the event-type (given by tpv.event.notify).

The function signature of the callback method for exact type matches looks like
    def callback(data, *extra_args)
and for regex matches like
    def callback(evtype, data, *extra_args)

where `data` contains the argument supplied to notify.

Usage example:

    @tpv.event.subscribe(type="user-denied", extra_args=('denied_template',))
    @tpv.event.subscribe(type="user-approved", extra_args=('approved_template',))
    def send_email(userdata, template):
        [ ... send email ... ]

    @tpv.event.subscribe(regex="user-.*")
    def send_whatever_email(evtype, userdata):
        [ ... ]

    '''
    def deco(f):
        global tpv_subscriber_exact, tpv_subscriber_regex

        if type is not None:
            tpv_subscriber_exact.setdefault(type, []).append((f, extra_args))
        elif regex is not None:
            tpv_subscriber_regex.setdefault(regex, []).append((f, extra_args))
        return f

    return deco



##
#
# Event sources logic

# aspect, which is applied to dicttrees and generates events on
# specific setitem calls

class hook(aspect.Aspect):
    '''Hook aspect fires events on __setitem__ in a dicttree.

As event data the branch is passed to the matching callback methods.

Config Keywords:

specs -- list of specs, like (<path>, <value>, <event-type>)

where

path       -- path to leaf in the dicttree
value      -- expected value, triggers event
event-type -- triggered event

Usage example

@tpv.event.hook([ ('/approval', 'granted', 'user-approved'),
                  ('/foo/bar/approval', 'granted', 'user-approved'),
                  ('/foo/baz/approval', 'denied', 'user-denied') ])
class NotifyingDict(OrderedDict):
    pass
    '''

    specs = aspect.config(None)

    # to be able to give translated specs to children, we internally
    # prefer a so called unrolled format, which is generated below by
    # unroll_specs. For the usage example above, it would look like
    #
    #   unrolled_specs = \
    #   dict(approval=('granted', 'user-approved'),
    #        foo     =[ ('/bar/approval', 'granted', 'user-approved'),
    #                   ('/baz/approval', 'denied', 'user-denied') ])

    @aspect.plumb
    def __init__(_next, self, *args, **kw):
        self.unrolled_specs = dict() \
                              if self.specs is None \
                              else unroll_specs(self.specs)

        _next(*args, **kw)

    @aspect.plumb
    def __getitem__(_next, self, key):
        val = _next(key)

        # if our spec wants to listen to a branch, we have to wrap
        # this branch in the hook as well, with the translated spec
        if isinstance(self.unrolled_specs.get(key, None), list):
            if not isinstance(val, dict):
                raise TypeError("hook aspect expected %s to be of type dict" % val)
            return hook(val, specs=self.unrolled_specs[key])

        return val

    @aspect.plumb
    def __setitem__(_next, self, key, val):
        _next(key, val)

        try:
            value, evtype = self.unrolled_specs.get(key, (None, None))
            if value == val:
                # a leaf has been set to an expected value, thus notify.
                # pass self (the current branch) as evdata. might be
                # useful in the callback.
                notify(evtype, self)
        except ValueError:
            # user must have set the value of a branch, that we have
            # been listening on. we'll keep on listening, anyway.
            pass



def unroll_specs(specs):
    '''Unroll the first layer of a spec of the branch/leaf mixing type

    [ ('/approval', 'granted', 'user-approved'),
      ('/foo/bar/approval', 'granted', 'user-approved'),
      ('/foo/baz/approval', 'denied', 'user-denied') ]
becomes
    unrolled_specs = \
        dict(approval=('granted', 'user-approved'),
             foo     =[ ('/bar/approval', 'granted', 'user-approved'),
                        ('/baz/approval', 'denied', 'user-denied') ])
    '''
    tree = dict()

    for path, value, evtype in specs:
        split = path[1:].split('/', 1)
        if len(split) < 2:
            # leaf
            tree[split[0]] = (value, evtype)
        else:
            # branch
            comp, rest = split
            tree.setdefault(comp, []).append( ('/' + rest, value, evtype) )

    return tree

# def unroll_spec(spec):
#     '''Unroll a spec completely in one go

#     [ ('/foo/bar', 'approval', 'granted', 'user-approved'),
#       ('/foo/baz', 'approval', 'denied', 'user-denied') ]
# becomes
#     unrolled_spec_list = \
#         dict(foo={ 'bar' : { 'approval': ('granted', 'user-approved') },
#                    'baz' : { 'approval': ('denied', 'user-denied') } })
#     '''

#     tree = dict()

#     for path, leaf, value, evtype in spec:
#         components = filter(None, path[1:].split('/'))

#         node = tree
#         for comp in components:
#             node = node.setdefault(comp, dict())

#         node[leaf] = (value, evtype)

#     return tree



# def unroll_spec_1st(spec):
#     '''Unroll the first layer of a spec of the separated branch/leaf type

#     [ ('/', 'approval', 'granted', 'user-approved'),
#       ('/foo/bar', 'approval', 'granted', 'user-approved'),
#       ('/foo/baz', 'approval', 'denied', 'user-denied') ]
# becomes
#     unrolled_spec_list = \
#         dict(approval=('granted', 'user-approved'),
#              foo     =[ ('/bar', 'approval', 'granted', 'user-approved'),
#                         ('/baz', 'approval', 'denied', 'user-denied') ])
#     '''

#     tree = dict()

#     for path, leaf, value, evtype in spec:
#         if path == '/':
#             # leaf
#             tree[leaf] = (value, evtype)
#             continue

#         # branch
#         comp = path[1:].split('/', 2)

#         # ''.join(comp[1:]) is a bit hacky, joins either an empty list
#         # or a one element list
#         tree.setdefault(comp[0], []).append(
#             ('/' + ''.join(comp[1:]), leaf, value, evtype)
#         )

#     return tree
