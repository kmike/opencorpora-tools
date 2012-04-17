# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import unittest
import tempfile
import shutil

import opencorpora

TEST_DATA = os.path.join(os.path.dirname(__file__), 'annot.opcorpora.test.xml')

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        cache_filename = os.path.join(self.temp_dir, 'corpora.cache')
        self.corpus = opencorpora.Corpora(TEST_DATA, cache_filename=cache_filename)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

class CorporaTest(BaseTest):

    def test_meta(self):
        self.assertEqual(self.corpus.catalog(), [
            (1, '"Частный корреспондент"'),
            (2, '00021 Школа злословия'),
            (3, '00022 Последнее восстание в Сеуле'),
            (4, '00023 За кота - ответишь!'),
        ])

    def test_raw_loading(self):
        loaded_raw = self.corpus._get_doc_by_raw_offset(3)
        loaded_line = self.corpus._get_doc_by_line_offset(3) # this is reliable
        self.assertEqual(loaded_raw, loaded_line)

    def test_single_doc_xml(self):
        xml = self.corpus._document_xml(3)
        tokens = xml.findall('paragraphs//token')
        self.assertEqual(tokens[17].get('text'), 'арт-группы')

    def test_doc_xml(self):
        doc = self.corpus.documents()[2]
        tokens = doc.tokens()
        self.assertTrue(tokens)
        self.assertEqual(tokens[17], 'арт-группы')


    def test_titles(self):
        titles = [doc.title() for doc in self.corpus.iterdocuments()]
        catalog_titles = list(dict(self.corpus.catalog()).values())
        self.assertEqual(titles, catalog_titles)

    def test_tokens(self):
        tokens = self.corpus.tokens()
        self.assertEqual(len(tokens), 2358)

        # check some random tokens
        self.assertEqual(tokens[344], 'социально-исторического')
        self.assertEqual(tokens[430], ':')
        self.assertEqual(tokens[967], 'Школа')
        self.assertEqual(tokens[2225], '«')
        self.assertEqual(tokens[2322], 'крэнк')

    def test_paras(self):
        paras = self.corpus.paras()
        self.assertEqual(len(paras), 41)

        for para in paras:
            self.assertTrue(para.tokens())
            self.assertTrue(para.sents())

    def test_sents(self):
        sents = self.corpus.sents()
        self.assertEqual(len(sents), 102)

        for sent in sents:
            self.assertTrue(sent.tokens())


class TextTest(BaseTest):

    def test_tokens(self):
        self.assertEqual(self.corpus.get_document(1).tokens(), [])

        tokens = self.corpus.get_document(2).tokens()

        self.assertEqual(len(tokens), 1027)
        self.assertEqual(tokens[9], 'градус')

    def test_sents(self):
        sents = self.corpus.get_document(2).sents()
        self.assertEqual(len(sents), 44)
        self.assertEqual(sents[1].as_text(), 'Сохранится ли градус дискуссии в новом сезоне?')


