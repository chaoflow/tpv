from __future__ import absolute_import

import os
import tpv.testing
import tpv.fs


class TestCase(tpv.testing.TestCase):
    def setUp(self):
        tpv.testing.TestCase.setUp(self)
        os.mkdir('directory')
        with open('file', 'w') as f:
            f.write('hello')
        os.symlink('file', 'link')
        self.root = tpv.fs.Directory('.')

    def test_directory_keys(self):
        self.assertEqual(self.root.keys(), ['directory', 'file', 'link'])
