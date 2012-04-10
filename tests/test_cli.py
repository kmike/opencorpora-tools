# -*- coding: utf-8 -*-
from __future__ import absolute_import
import mock
import unittest
import tempfile
from opencorpora import cli

class CliTest(unittest.TestCase):

    @mock.patch('opencorpora.cli.urlopen')
    def test_download(self, urlopen):
        urlopen.return_value.read.return_value = ''
        with tempfile.NamedTemporaryFile() as f:
            class Args(object):
                output = f.name
                decompress = False
                url = ''
            args = Args()
            cli.download(args)
