# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
from collections import namedtuple
from .compat import ElementTree, OrderedDict
from . import xml_utils

_TextMeta = namedtuple('_TextMeta', 'title bounds')

class OpenCorporaBase(object):
    """
    Common interface for OpenCorpora objects.
    """
    def iterparas(self):
        raise NotImplementedError()

    def itertokens(self):
        raise NotImplementedError()

    def itersents(self):
        raise NotImplementedError()


    def paras(self):
        return list(self.iterparas())

    def tokens(self):
        return list(self.itertokens())

    def sents(self):
        return list(self.itersents())


    def as_text(self):
        return ' '.join(self.itertokens())


class Sentence(OpenCorporaBase):
    """
    Sentence.
    """
    def __init__(self, xml):
        self.root = xml

    def itertokens(self):
        for token in self.root.findall('tokens//token'):
            yield token.get('text')

    def source(self):
        return self.root.find('source').text

    def as_text(self):
        return self.source()


class Paragraph(OpenCorporaBase):
    """
    Text paragraph.
    """
    def __init__(self, xml):
        self.root = xml

    def itertokens(self):
        for token in self.root.findall('sentence//token'):
            yield token.get('text')

    def itersents(self):
        for sent in self.root.findall('sentence'):
            yield Sentence(sent)

    def as_text(self):
        return ' '.join(sent.as_text() for sent in self.itersents())


class Text(OpenCorporaBase):
    """
    Single OpenCorpora text.
    """
    def __init__(self, xml):
        self.root = xml

    def title(self):
        return self.root.get('name')

    def itertokens(self):
        for token in self.root.findall('paragraphs//token'):
            yield token.get('text')

    def iterparas(self):
        for para in self.root.findall('paragraphs/paragraph'):
            yield Paragraph(para)

    def itersents(self):
        for sent in self.root.findall('paragraphs//sentence'):
            yield Sentence(sent)

    def as_text(self):
        return "\n\n".join(para.as_text() for para in self.iterparas())


class Corpora(OpenCorporaBase):
    """
    OpenCorpora.ru corpora reader. Provides fast access to individual
    texts without loading and parsing the whole XML; is capable of iterating
    over individual paragraphs, sentences and tokens without loading
    all data to memory.
    """
    def __init__(self, filename):
        self.filename = filename
        self._text_meta = OrderedDict()
        self._populate_text_meta()

    def catalog(self):
        """
        Returns information about texts in corpora:
        a list of tuples (text_id, text_title).
        """
        return [(text_id, self._text_meta[text_id].title) for text_id in self._text_meta]

    def get_text(self, text_id):
        """
        Returns Text object for a given text_id.
        """
        return Text(self._text_xml(text_id))

    def itertokens(self):
        """
        Returns an iterator over corpus tokens.
        """
        for token in xml_utils.iterparse(self.filename, 'token', clear=True):
            yield token.get('text')

    def itersents(self):
        for sent in xml_utils.iterparse(self.filename, 'sentence'):
            yield Sentence(sent)

    def iterparas(self):
        for para in xml_utils.iterparse(self.filename, 'paragraph'):
            yield Paragraph(para)


    def itertexts(self):
        """
        Returns an iterator over corpus texts.
        """
        for text in xml_utils.iterparse(self.filename, 'text'):
            yield Text(text)

    def texts(self):
        """
        Returns a list of all corpus texts.

        XXX: it can be very slow and memory-consuming; use
        itertexts of get_text when possible.
        """
        return list(self.itertexts())

    def _populate_text_meta(self):
        """
        Populates texts meta information cache for fast lookups.
        """
        bounds_iter = xml_utils.bounds(self.filename,
            r'<text id="(\d+)"[^>]*name="([^"]*)"',
            r'</text>',
        )
        for match, bounds in bounds_iter:
            text_id, title = int(match.group(1)), match.group(2)
            title = xml_utils.unescape_attribute(title)
            self._text_meta[text_id] = _TextMeta(title, bounds)

    def _text_xml(self, text_id):
        """
        Returns xml Element for the text text_id.
        """
        text_str = self._get_text_by_raw_offset(text_id)
        return ElementTree.XML(text_str.encode('utf8'))

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
