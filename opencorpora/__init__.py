# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import os
import itertools
import fnmatch
from collections import namedtuple
from opencorpora import compat, xml_utils

_DocumentMeta = namedtuple('_DocumentMeta', 'title bounds categories')

def _xml_tags_to_list(l_element):
    return [tag.get('v') for tag in l_element.getchildren()]

def _token_info(token_element):
    for lemma in token_element.findall('*//l'):
        yield lemma.get('t'), _xml_tags_to_list(lemma)

def _first_tags(token_element):
    lemma = token_element.find('*//l')
    if lemma is None:
        return None, []
    return lemma.get('t'), _xml_tags_to_list(lemma)

def _make_iterable(obj, default=None):
    if obj is None:
        return default or []
    if isinstance(obj, (compat.string_types, compat.integer_types)):
        return [obj]
    return obj

def _some_items_match(items, patterns):
    return any(
        fnmatch.fnmatchcase(item, pattern)
        for item in items
        for pattern in patterns
    )

class _OpenCorporaBase(object):
    """
    Common interface for OpenCorpora objects.
    """
    def _itertokens(self):
        # subclass should define self.root Element for this to work
        return self.root.findall('*//token')

    def iterwords(self):
        return (token.get('text') for token in self._itertokens())

    def itersents(self):
        raise NotImplementedError()

    def iterparas(self):
        raise NotImplementedError()


    def iter_tagged_words(self):
        for token in self._itertokens():
            word = token.get('text')
            lemma, tags = _first_tags(token)
            yield word, ",".join(tags)

    def iter_tagged_sents(self):
        return (sent.tagged_words() for sent in self.itersents())

    def iter_tagged_paras(self):
        return (para.tagged_sents() for para in self.iterparas())


    def words(self):
        return list(self.iterwords())

    def sents(self):
        return list(self.itersents())

    def paras(self):
        return list(self.iterparas())

    def raw(self):
        return self.as_text()


    def tagged_words(self):
        return list(self.iter_tagged_words())

    def tagged_sents(self):
        return list(self.iter_tagged_sents())

    def tagged_paras(self):
        return list(self.iter_tagged_paras())

    def as_text(self):
        return ' '.join(self.iterwords())

    # XXX: does this work under windows?
    @compat.utf8_for_PY2
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.as_text())

    @compat.utf8_for_PY2
    def __str__(self):
        return self.as_text()

    def __unicode__(self):
        return self.as_text()

class Sentence(_OpenCorporaBase):
    """
    Sentence.
    """
    def __init__(self, xml):
        self.root = xml

    def source(self):
        return self.root.find('source').text

    def as_text(self):
        return self.source()

    def __len__(self):
        return len(self.words())

    def __getitem__(self, key):
        return self.words()[key]

    def __iter__(self):
        return (word for word in self.iterwords())

class Paragraph(_OpenCorporaBase):
    """
    Text paragraph.
    """
    def __init__(self, xml):
        self.root = xml

    def itersents(self):
        return compat.imap(Sentence, self.root.findall('sentence'))

    def as_text(self):
        return ' '.join(sent.as_text() for sent in self.itersents())

    def __len__(self):
        return len(self.sents())

    def __getitem__(self, key):
        return self.sents()[key]

    __iter__ = itersents

class Document(_OpenCorporaBase):
    """
    Single OpenCorpora document.
    """
    def __init__(self, xml):
        self.root = xml

    def title(self):
        return self.root.get('name')

    def categories(self):
        return [tag.text for tag in self.root.findall('tags//tag')]

    def iterparas(self):
        return compat.imap(Paragraph, self.root.findall('paragraphs/paragraph'))

    def itersents(self):
        return compat.imap(Sentence, self.root.findall('paragraphs//sentence'))

    def as_text(self):
        return "\n\n".join(para.as_text() for para in self.iterparas())

    def __len__(self):
        return len(self.paras())

    def __getitem__(self, key):
        return self.paras()[key]

    @compat.utf8_for_PY2
    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self.title())

    __iter__ = iterparas


class Corpora(object):
    """
    OpenCorpora.ru corpora reader. Provides fast access to individual
    documents without loading and parsing the whole XML; is capable of iterating
    over individual paragraphs, sentences and tokens without loading
    all data to memory.
    """
    def __init__(self, filename, cache_filename=None, use_cache=True):
        self.filename = filename
        self.use_cache = use_cache
        self._document_meta = None
        self._cache_filename = cache_filename or filename+'.~'

    def readme(self):
        return self.__doc__

    def raw(self, fileids=None, categories=None):
        return " ".join(self.iterwords(fileids, categories))

    def words(self, fileids=None, categories=None):
        return list(self.iterwords(fileids, categories))

    def paras(self, fileids=None, categories=None):
        return list(self.iterparas(fileids, categories))

    def sents(self, fileids=None, categories=None):
        return list(self.itersents(fileids, categories))

    def tagged_words(self, fileids=None, categories=None):
        return list(self.iter_tagged_words(fileids, categories))

    def tagged_paras(self, fileids=None, categories=None):
        return list(self.iter_tagged_paras(fileids, categories))

    def tagged_sents(self, fileids=None, categories=None):
        return list(self.iter_tagged_sents(fileids, categories))

    def documents(self, fileids=None, categories=None):
        """
        Returns a list of corpus documents.

        XXX: it can be very slow and memory-consuming if fileids
        and categories are both None; use iterdocuments or
        pass fileids/categories when possible.
        """
        return list(self.iterdocuments(fileids, categories))

    def iter_tagged_words(self, fileids=None, categories=None):
        if fileids is None and categories is None:
            tokens = xml_utils.iterparse(self.filename, 'token', clear=False)
            for token in tokens:
                word = token.get('text')
                lemma, tags = _first_tags(token)
                yield word, ",".join(tags)
                token.clear()
        else:
            docs = self.iterdocuments(fileids, categories)
            words = itertools.chain(*(doc.iter_tagged_words() for doc in docs))
            for word in words:
                yield word

    def iter_tagged_paras(self, fileids=None, categories=None):
        paras = self.iterparas(fileids, categories)
        return (para.tagged_sents() for para in paras)

    def iter_tagged_sents(self, fileids=None, categories=None):
        sents = self.itersents(fileids, categories)
        return (sent.tagged_words() for sent in sents)

    def iterwords(self, fileids=None, categories=None):
        if fileids is None and categories is None:
            xml_tokens = xml_utils.iterparse(self.filename, 'token', clear=True)
            return (token.get('text') for token in xml_tokens)

        docs = self.iterdocuments(fileids, categories)
        return itertools.chain(*(doc.iterwords() for doc in docs))

    def itersents(self, fileids=None, categories=None):
        if fileids is None and categories is None:
            xml_sents = xml_utils.iterparse(self.filename, 'sentence')
            return compat.imap(Sentence, xml_sents)

        docs = self.iterdocuments(fileids, categories)
        return itertools.chain(*(doc.itersents() for doc in docs))

    def iterparas(self, fileids=None, categories=None):
        if fileids is None and categories is None:
            xml_paras = xml_utils.iterparse(self.filename, 'paragraph')
            return compat.imap(Paragraph, xml_paras)

        docs = self.iterdocuments(fileids, categories)
        return itertools.chain(*(doc.iterparas() for doc in docs))

    def iterdocuments(self, fileids=None, categories=None):
        """
        Returns an iterator over corpus documents.
        """
        if fileids is None and categories is None:
            return compat.imap(Document, xml_utils.iterparse(self.filename, 'text'))

        doc_ids = self._filter_ids(fileids, categories)
        return (self.get_document(doc_id) for doc_id in doc_ids)

    def fileids(self, categories=None):
        return list(self._filter_ids(None, categories))

    def categories(self, fileids=None, patterns=None):
        meta = self._get_meta()
        fileids = _make_iterable(fileids, meta.keys())

        result = sorted(list(set(
            cat for cat in itertools.chain(*(
                meta[str(doc_id)].categories for doc_id in fileids
            ))
        )))

        if patterns:
            patterns = _make_iterable(patterns)
            result = [cat for cat in result if _some_items_match([cat], patterns)]

        return result

    def catalog(self, categories=None):
        """
        Returns information about documents in corpora:
        a list of tuples (doc_id, doc_title).
        """
        ids = self._filter_ids(None, categories)
        doc_meta = self._get_meta()
        return [(doc_id, doc_meta[doc_id].title) for doc_id in ids]

    def get_document(self, doc_id):
        """
        Returns Document object for a given doc_id.
        This is also available as corpus[doc_id] and corpus.documents(doc_id).
        """
        return Document(self._document_xml(doc_id))

    def _filter_ids(self, fileids=None, categories=None):
        meta = self._get_meta()
        fileids = _make_iterable(fileids, meta.keys())

        if categories is None:
            return map(str, fileids)

        category_patterns = _make_iterable(categories)
        return (doc_id for doc_id in fileids
                if _some_items_match(meta[doc_id].categories, category_patterns))

    def _get_meta(self):

        if self._document_meta is None and self.use_cache:
            self._load_meta_cache()

        if self._document_meta is None:
            self._document_meta = self._compute_document_meta()
            if self.use_cache:
                self._create_meta_cache()

        return self._document_meta

    def _create_meta_cache(self):
        """
        Tries to dump metadata to a file.
        """
        try:
            with open(self._cache_filename, 'wb') as f:
                compat.pickle.dump(self._document_meta, f, 1)
        except (IOError, compat.pickle.PickleError):
            pass

    def _load_meta_cache(self):
        """
        Tries to load metadata from file.
        """
        try:
            if os.path.getmtime(self.filename) > os.path.getmtime(self._cache_filename):
                os.remove(self._cache_filename)
            else:
                with open(self._cache_filename, 'rb') as f:
                    self._document_meta = compat.pickle.load(f)
        except (OSError, IOError, compat.pickle.PickleError, ImportError, AttributeError):
            pass

    def _compute_document_meta(self):
        """
        Returns documents meta information that can
        be used for fast document lookups. Meta information
        consists of documents titles, categories and positions
        in file.
        """
        meta = compat.OrderedDict()
        bounds_iter = xml_utils.bounds(self.filename,
            r'<text id="(\d+)"[^>]*name="([^"]*)"',
            r'</text>',
        )
        for match, bounds in bounds_iter:
            doc_id, title = str(match.group(1)), match.group(2)
            title = xml_utils.unescape_attribute(title)

            # cache categories
            xml = xml_utils.load_chunk(self.filename, bounds)
            doc = Document(compat.ElementTree.XML(xml.encode('utf8')))

            meta[doc_id] = _DocumentMeta(title, bounds, doc.categories())
        return meta

    def _document_xml(self, doc_id):
        """
        Returns xml Element for the document document_id.
        """
        doc_str = self._get_doc_by_raw_offset(str(doc_id))
        return compat.ElementTree.XML(doc_str.encode('utf8'))

    def _get_doc_by_raw_offset(self, doc_id):
        """
        Loads document from xml using bytes offset information.
        XXX: this is not tested under Windows.
        """
        bounds = self._get_meta()[str(doc_id)].bounds
        return xml_utils.load_chunk(self.filename, bounds)

    def _get_doc_by_line_offset(self, doc_id):
        """
        Loads document from xml using line offset information.
        This is much slower than _get_doc_by_raw_offset but should
        work everywhere.
        """
        bounds = self._get_meta()[str(doc_id)].bounds
        return xml_utils.load_chunk(self.filename, bounds, slow=True)

    __getitem__ = get_document
    __iter__ = iterdocuments
