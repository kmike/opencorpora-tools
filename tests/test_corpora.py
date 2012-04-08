# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import unittest
from opencorpora.compat import ElementTree

import opencorpora

TEST_DATA = os.path.join(os.path.dirname(__file__), 'annot.opcorpora.test.xml')

class CorporaTest(unittest.TestCase):

    def setUp(self):
        self.corpus = opencorpora.Corpora(TEST_DATA)

    def test_text_meta(self):
        self.assertEqual(self.corpus.catalog(), [
            ('1', '&quot;Частный корреспондент&quot;'),
            ('2', '00021 Школа злословия'),
            ('3', '00022 Последнее восстание в Сеуле'),
            ('4', '00023 За кота - ответишь!'),
        ])

    def test_raw_loading(self):
        loaded_raw = self.corpus._get_text_by_raw_offset('3')
        loaded_line = self.corpus._get_text_by_line_offset('3') # this is reliable
        self.assertEqual(loaded_raw, loaded_line)

    def test_text_xml(self):
        xml = self.corpus.get_text_xml('3')
        tokens = xml.findall('paragraphs//token')
        self.assertEqual(tokens[17].get('text'), 'арт-группы')

    def test_tokens(self):
        tokens = list(self.corpus.itertokens())
        self.assertEqual(len(tokens), 2358)

        # check some random tokens
        self.assertEqual(tokens[344], 'социально-исторического')
        self.assertEqual(tokens[430], ':')
        self.assertEqual(tokens[967], 'Школа')
        self.assertEqual(tokens[2225], '«')
        self.assertEqual(tokens[2322], 'крэнк')
