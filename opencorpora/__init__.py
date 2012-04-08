# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import re
import codecs
from collections import namedtuple
from .compat import ElementTree, OrderedDict

TextOffset = namedtuple('TextOffset', 'line_start line_end raw_start raw_end')

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
        for text_id, offset in self._text_offsets():
            self._text_meta[text_id] = offset

    def _text_offsets(self):
        START_RE = re.compile(r'<text id="(\d+)"')
        text_id, line_start, line_end, raw_start, raw_end = None, None, None, None, None
        offset = 0
        with open(self.filename, 'rb') as f:
            for index, line in enumerate(f):
                line_text = line.decode('utf8')
                mo = re.match(START_RE, line_text)
                if mo:
                    text_id, line_start, raw_start = mo.group(1), index, offset

                offset += len(line)

                if '</text>' in line_text:
                    yield text_id, TextOffset(line_start, index, raw_start, offset)
                    text_id, line_start, line_end, raw_start, raw_end = None, None, None, None, None

    def _get_text_by_raw_offset(self, text_id):
        """
        Loads text from xml using bytes offset information.
        XXX: this is not tested under Windows.
        """
        offset = self._text_meta[text_id]
        with open(self.filename, 'rb') as f:
            f.seek(offset.raw_start)
            return f.read(offset.raw_end-offset.raw_start).decode('utf8')

    def _get_text_by_line_offset(self, text_id):
        """
        Loads text from xml using line offset information.
        This is much slower than _get_text_by_raw_offset but should
        work everywhere.
        """
        offset = self._text_meta[text_id]
        lines = []
        with codecs.open(self.filename, 'rb', 'utf8') as f:
            for index, line in enumerate(f):
                if index >= offset.line_start:
                    lines.append(line)
                if index >= offset.line_end:
                    break
        return ''.join(lines)

    def get_text_ids(self):
        return list(self._text_meta.keys())

    def get_text_xml(self, text_id):
        """
        Returns xml Element for the text text_id.
        """
        text_str = self._get_text_by_raw_offset(str(text_id))
        return ElementTree.XML(text_str.encode('utf8'))
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
