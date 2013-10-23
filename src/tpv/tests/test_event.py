from ..testing import unittest
from ..ordereddict import OrderedDict

from .. import event
from ..event import tpv_subscriber_exact, tpv_subscriber_regex


class EventTestBase(unittest.TestCase):
    def tearDown(self):
        tpv_subscriber_exact.clear()
        tpv_subscriber_regex.clear()


class TestSubscribeNotify(EventTestBase):
    def test_subscribe(self):
        @event.subscribe(type="user-approved")
        @event.subscribe(type="user-approved", extra_args=("foo", "bar"))
        def approved_callback(userdata, *extra_args):
            pass

        self.assertTrue('user-approved' in tpv_subscriber_exact)
        self.assertEqual(len(tpv_subscriber_exact['user-approved']), 2)
        self.assertTrue((approved_callback, ())
                        in tpv_subscriber_exact['user-approved'])
        self.assertTrue((approved_callback, ("foo","bar"))
                        in tpv_subscriber_exact['user-approved'])

        @event.subscribe(regex="user-*", extra_args=("foo", "bar"))
        def user_callback(evtype, evdata):
            pass

        self.assertTrue('user-*' in tpv_subscriber_regex)
        self.assertTrue((user_callback, ("foo", "bar"))
                        in tpv_subscriber_regex['user-*'])

    def test_notify_exact(self):
        state = dict()

        @event.subscribe(type="user-approved")
        @event.subscribe(type="user-approved", extra_args=("foo", "bar"))
        def approved_callback(userdata, *extra_args):
            state.setdefault('approved', []).append((userdata, extra_args))

        @event.subscribe(type="user-denied")
        def denied_callback(userdata):
            state.setdefault('denied', []).append((userdata, extra_args))

        # notify
        event.notify('user-approved', "baz")

        self.assertTrue('approved' in state)
        self.assertFalse('denied' in state)

        self.assertTrue(("baz", ()) in state['approved'])
        self.assertTrue(("baz", ("foo", "bar")) in state['approved'])

        self.assertFalse(("zab", ()) in state['approved'])
        self.assertEqual(len(state['approved']), 2)

    def test_notify_regex(self):
        state = dict()

        @event.subscribe(regex="user-*", extra_args=("foo",))
        def user_callback(evtype, userdata, *extra_args):
            state.setdefault('user', []).append((evtype, userdata, extra_args))

        @event.subscribe(regex="group-*")
        def group_callback(evtype, groupdata, extra_args):
            state.setdefault('group', []).append((evtype, groupdata, extra_args))

        # notify
        event.notify('user-approved', "baz")

        self.assertTrue('user' in state)
        self.assertFalse('group' in state)

        self.assertTrue(("user-approved", "baz", ("foo",)) in state['user'])



class TestEventHook(EventTestBase):
    def setUp(self):
        @event.hook(specs=[('/approval', 'granted', 'user-approved'),
                           ('/foo/bar/approval', 'granted', 'user-approved'),
                           ('/foo/baz/approval', 'denied', 'user-denied')])
        class NotifyingDict(OrderedDict):
            pass

        tree = OrderedDict(path='/', approval=None,
                           foo=OrderedDict(path='/foo',
                                           bar=OrderedDict(path='/foo/bar',
                                                           approval=None),
                                           baz=OrderedDict(path='/foo/baz',
                                                           approval=None)))
        self.tree = NotifyingDict(tree)

        self.state = dict()
        @event.subscribe(regex="user-*", extra_args=("foo",))
        def user_callback(evtype, data, *extra_args):
            self.state.setdefault(evtype, []).append((data['path'],
                                                      extra_args[0]))


    def test_hook_fires(self):
        self.tree['approval'] = 'granted'

        self.assertTrue('user-approved' in self.state)
        self.assertFalse('user-denied' in self.state)

        self.assertTrue(('/', "foo") in self.state['user-approved'])

        self.tree['foo']['baz']['approval'] = 'denied'
        self.assertTrue('user-denied' in self.state)
        self.assertTrue(('/foo/baz', "foo") in self.state['user-denied'])

    def test_hook_doesnt_fire(self):
        self.tree['approval'] = 'not granted'
        self.assertEqual(len(self.state), 0)

        self.tree['otherleaf'] = 'granted'
        self.assertEqual(len(self.state), 0)

        self.tree['foo']['bar']['approval'] = 'not granted'
        self.assertEqual(len(self.state), 0)

        self.tree['foo']['baz']['approval'] = 'granted'
        self.assertEqual(len(self.state), 0)
