# -*- coding: utf-8 -*-
"""
Another OpenCorpora corpus reader, which loads
the whole XML corpus in memory and provides a nice API
using lxml Element wrappers.
"""
from __future__ import absolute_import
from lxml import etree


def load(source):
    """
    Load OpenCorpora corpus.

    The ``source`` can be any of the following:

    - a file name/path
    - a file object
    - a file-like object
    - a URL using the HTTP or FTP protocol

    """
    parser = get_xml_parser()
    return etree.parse(source, parser=parser).getroot()


def get_xml_parser():
    lookup = etree.ElementNamespaceClassLookup()
    parser = etree.XMLParser()
    parser.set_element_class_lookup(lookup)

    namespace = lookup.get_namespace('')
    namespace['text'] = Doc
    namespace['annotation'] = Corpus
    namespace['paragraph'] = Paragraph
    namespace['sentence'] = Sentence
    namespace['token'] = Token
    namespace['l'] = Parse

    return parser


class Query(object):
    def __init__(self, query_func):
        self.query_func = query_func

    def __get__(self, obj, objtype):
        return self.query_func(obj)


class Xpath(object):
    def __init__(self, xpath):
        self.xpath = xpath

    def __get__(self, obj, objtype):
        return obj.xpath(self.xpath)


def Attrib(name):
    return Query(lambda obj: obj.get(name))


def Children(query):
    return Query(lambda obj: obj.findall(query))


def ChildrenText(query):
    return Query(lambda obj: [el.text for el in obj.findall(query)])


def NumTokens():
    def get_num_tokens(obj):
        if getattr(obj, '_num_tokens_cached', None) is None:
            obj._num_tokens_cached = int(obj.xpath('count(.//token)'))
        return obj._num_tokens_cached
    return Query(get_num_tokens)


class TokensIter(object):
    def __getitem__(self, item):
        return self.tokens[item]

    def __iter__(self):
        return iter(self.tokens)


class Corpus(etree.ElementBase):
    version = Attrib('version')
    revision = Attrib('revision')
    docs = Children('text')
    paragraphs = Children('text/paragraphs/paragraph')
    sentences = Children('text/paragraphs/paragraph/sentence')
    tokens = Children('text/paragraphs/paragraph/sentence/tokens/token')
    num_tokens = NumTokens()

    def __repr__(self):
        return "<Corpus revision=%s docs:%s tokens:%s>" % (
            self.revision, len(self.docs), self.num_tokens
        )


class Doc(TokensIter, etree.ElementBase):
    id = Attrib('id')
    name = Attrib('name')
    parent = Attrib('parent')
    tags = ChildrenText('tags/tag')
    paragraphs = Children('paragraphs/paragraph')
    sentences = Children('paragraphs/paragraph/sentence')
    tokens = Children('paragraphs/paragraph/sentence/tokens/token')
    num_tokens = NumTokens()

    @property
    def source(self):
        return "\n\n".join(p.source for p in self.paragraphs)

    def __repr__(self):
        return "<Doc id=%s tokens:%s name=%r>" % (
            self.id, self.num_tokens, self.name,
        )


class Paragraph(TokensIter, etree.ElementBase):
    id = Attrib('id')
    sentences = Children('sentence')
    tokens = Children('sentence/tokens/token')
    num_tokens = NumTokens()

    @property
    def source(self):
        return "  ".join(s.source for s in self.sentences)

    def __repr__(self):
        return "<Paragraph id=%s source=%r>" % (self.id, self.source)


class Sentence(TokensIter, etree.ElementBase):
    id = Attrib('id')
    source = Query(lambda obj: obj.find('source').text)
    tokens = Children('tokens/token')
    num_tokens = NumTokens()

    def __repr__(self):
        return "<Sentence id=%s source=%r>" % (self.id, self.source)


class Token(etree.ElementBase):
    id = Attrib('id')
    source = Attrib('text')
    rev_id = Query(lambda obj: obj.find("tfr").get("rev_id"))
    parses = Children('tfr/v/l')
    parse = Query(lambda obj: obj.find('tfr/v/l'))

    @property
    def lemma(self):
        return self.parse.lemma

    @property
    def grammemes(self):
        return self.parse.grammemes

    def __repr__(self):
        return "<Token id=%s source=%r>" % (self.id, self.source)


class Parse(etree.ElementBase):
    id = Attrib('id')
    lemma = Attrib('t')
    grammemes = Xpath("g/@v")

    def __repr__(self):
        return "<Parse id=%s lemma=%s grammemes=%s>" % (self.id, self.lemma, self.grammemes)
