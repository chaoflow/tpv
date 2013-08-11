import os
import shutil
import sys
import traceback

from . import unittest


class TestCase(unittest.TestCase):
    TEST_ROOT = os.getcwdu()
    KEEP_FAILED = bool(os.environ.get('KEEP_FAILED'))

    @property
    def testdir(self):
        return os.path.sep.join(['var', self.id()])

    def setUp(self):
        try:
            self._create_and_switch_to_testdir()
            self._setUp()
        except Exception, e:
            # XXX: working around nose to get immediate exception
            # output, not collected after all tests are run
            sys.stderr.write("""
======================================================================
Error setting up testcase: %s
----------------------------------------------------------------------
%s
""" % (str(e), traceback.format_exc()))
            TestCase.tearDown(self)
            raise e

    def _setUp(self):
        """this is to enable tpv.*.testing to do more complex stuff

        If something goes wrong debugging is easier and things will
        still be cleaned up.

        """

    def tearDown(self):
        self._remove_testdir_and_switch_back_to_testroot()

    def _create_and_switch_to_testdir(self):
        os.mkdir(self.testdir)
        os.chdir(self.testdir)

    def _remove_testdir_and_switch_back_to_testroot(self):
        successful = sys.exc_info() == (None, None, None)
        os.chdir(self.TEST_ROOT)
        if successful or not self.KEEP_FAILED:
            shutil.rmtree(self.testdir)
