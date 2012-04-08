# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import os
import unittest
from opencorpora.compat import ElementTree

import opencorpora

TEST_DATA = os.path.join(os.path.dirname(__file__), 'annot.opcorpora.test.xml')

class CorporaTest(unittest.TestCase):

    def setUp(self):
        self.corpus = opencorpora.Corpora(TEST_DATA)

    def test_text_meta(self):
        self.assertEqual(self.corpus.get_text_ids(), ['1', '2', '3', '4'])

    def test_raw_loading(self):
        loaded_raw = self.corpus._get_text_by_raw_offset('3')
        loaded_line = self.corpus._get_text_by_line_offset('3') # this is reliable
        self.assertEqual(loaded_raw, loaded_line)

    def test_text_xml(self):
        xml = self.corpus.get_text_xml('3')
        #print(ElementTree.tostring(xml, encoding='utf8'))
        #print(xml.xpath('//token[@id="1346"]'))

#    def test_get_text(self):
#        print
#        print self.reader._texts
#        print self.reader.get_text_raw('2')