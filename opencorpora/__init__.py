# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import re
from collections import namedtuple
from .compat import ElementTree, OrderedDict
from . import xml_utils

TextMeta = namedtuple('TextMeta', 'title bounds')

class Corpora(object):
    """
    Opencorpora.ru corpora reader. Provides fast access to individual
    texts without loading and parsing the whole XML; is capable of iterating
    over individual paragraphs, sentences and tokens without loading
    all data to memory.
    """
    def __init__(self, filename):
        self.filename = filename
        self._text_meta = OrderedDict()
        self._populate_text_meta()

    def _populate_text_meta(self):
        """
        Populates texts meta information cache for fast lookups.
        """
        bounds_iter = xml_utils.bounds(self.filename,
            r'<text id="(\d+)"[^>]*name="([^"]*)"',
            r'</text>',
        )
        for match, bounds in bounds_iter:
            text_id, title = match.group(1), match.group(2)
            self._text_meta[text_id] = TextMeta(title, bounds)

    def _get_text_by_raw_offset(self, text_id):
        """
        Loads text from xml using bytes offset information.
        XXX: this is not tested under Windows.
        """
        bounds = self._text_meta[text_id].bounds
        return xml_utils.load_chunk(self.filename, bounds)

    def _get_text_by_line_offset(self, text_id):
        """
        Loads text from xml using line offset information.
        This is much slower than _get_text_by_raw_offset but should
        work everywhere.
        """
        bounds = self._text_meta[text_id].bounds
        return xml_utils.load_chunk(self.filename, bounds, slow=True)

    def catalog(self):
        """
        Returns information about texts in corpora:
        a list of tuples (text_id, text_title).
        """
        return [(text_id, self._text_meta[text_id].title) for text_id in self._text_meta]

    def get_text_xml(self, text_id):
        """
        Returns xml Element for the text text_id.
        """
        text_str = self._get_text_by_raw_offset(str(text_id))
        return ElementTree.XML(text_str.encode('utf8'))

    def itertokens(self):
        """
        Returns an iterator over corpus tokens.
        """
        for token in xml_utils.iterparse(self.filename, 'token'):
            yield token.get('text')

    def tokens(self):
        """
        Returns a list of corpus tokens (this can be slow).
        """
        return list(self.tokens())


#
#    def words(self):
#        # list of str
#        pass
#
#    def sents(self):
#        # list of (list of str)
#        pass
#
#    def paras(self):
#        #list of (list of (list of str))
#        pass
#
#    def tagged_words(self):
#        # list of (str,str) tuple
#        pass
#
#    def tagged_sents(self):
#        # list of (list of (str,str))
#        pass
#
#    def tagged_paras(self):
#        # list of (list of (list of (str,str)))
#        pass
#
