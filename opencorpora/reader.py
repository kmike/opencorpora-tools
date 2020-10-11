# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import functools
import itertools
import fnmatch
from collections import namedtuple, OrderedDict
from opencorpora import compat, xml_utils
from opencorpora.compat import imap, text_type


def make_iterable(obj, default=None):
    """ Ensure obj is iterable. """
    if obj is None:
        return default or []
    if isinstance(obj, (compat.string_types, compat.integer_types)):
        return [obj]
    return obj


def some_items_match(items, patterns):
    return any(
        fnmatch.fnmatchcase(item, pattern)
        for item in items
        for pattern in patterns
    )


def _sentence_source(sent_elem):
    return text_type(sent_elem.find('source').text)


def _sentence_words(sent_elem):
    return [text_type(tok.get('text')) for tok in sent_elem.findall('*//token')]


def _sentence_tagged_words(sent_elem):
    res = []
    for tok in sent_elem.findall('*//token'):
        text = text_type(tok.get('text'))
        parse = tok.find('*//l')
        tag = text_type(',').join(_grammemes(parse))
        res.append((text, tag))
    return res


def _sentence_parsed_words(sent_elem):
    res = []
    for tok in sent_elem.findall('*//token'):
        text = text_type(tok.get('text'))
        parses = tok.findall('*//l')
        annotations = [
            (text_type(p.get('t')), text_type(',').join(_grammemes(p)))
            for p in parses
        ]
        res.append((text, annotations))
    return res


def _grammemes(l_element):
    return [text_type(grammeme.get('v'))
            for grammeme in list(l_element)]


def non_iterative(func):
    @functools.wraps(func)
    def res(*args, **kwargs):
        return list(func(*args, **kwargs))
    return res


class Document(object):
    """
    Single OpenCorpora document.
    """
    def __init__(self, xml):
        self.root = xml

    def _xml_sents(self):
        return self.root.findall('*//sentence')

    def _xml_paras(self):
        return self.root.findall('*//paragraph')

    def iter_sents(self):
        return imap(_sentence_words, self._xml_sents())

    def iter_raw_sents(self):
        return imap(_sentence_source, self._xml_sents())

    def iter_tagged_sents(self):
        return imap(_sentence_tagged_words, self._xml_sents())

    def iter_parsed_sents(self):
        return imap(_sentence_parsed_words, self._xml_sents())

    def iter_paras(self):
        for para_elem in self._xml_paras():
            yield [_sentence_words(s) for s in para_elem.findall('sentence')]

    def iter_raw_paras(self):
        for para_elem in self._xml_paras():
            yield " ".join(_sentence_source(s) for s in para_elem.findall('sentence'))

    def iter_tagged_paras(self):
        for para_elem in self._xml_paras():
            yield [_sentence_tagged_words(s) for s in para_elem.findall('sentence')]

    def iter_parsed_paras(self):
        for para_elem in self._xml_paras():
            yield [_sentence_parsed_words(s) for s in para_elem.findall('sentence')]

    def iter_words(self):
        return itertools.chain(*self.iter_sents())

    def iter_tagged_words(self):
        return itertools.chain(*self.iter_tagged_sents())

    def iter_parsed_words(self):
        return itertools.chain(*self.iter_parsed_sents())

    sents = non_iterative(iter_sents)
    raw_sents = non_iterative(iter_raw_sents)
    tagged_sents = non_iterative(iter_tagged_sents)
    parsed_sents = non_iterative(iter_parsed_sents)
    paras = non_iterative(iter_paras)
    raw_paras = non_iterative(iter_raw_paras)
    tagged_paras = non_iterative(iter_tagged_paras)
    parsed_paras = non_iterative(iter_parsed_paras)
    words = non_iterative(iter_words)
    tagged_words = non_iterative(iter_tagged_words)
    parsed_words = non_iterative(iter_parsed_words)

    # misc
    def title(self):
        return text_type(self.root.get('name'))

    def categories(self):
        return [text_type(tag.text) for tag in self.root.findall('tags//tag')]

    def raw(self):
        return "\n\n".join(self.iter_raw_paras())

    @compat.utf8_for_PY2
    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self.title())

    def destroy(self):
        self.root.clear()


_DocumentMeta = namedtuple('_DocumentMeta', 'title bounds categories')


def _from_documents(doc_method_name):
    def method(self, fileids=None, categories=None):
        return self._doc_iterator(fileids, categories, doc_method_name)
    method.__name__ = str(doc_method_name)
    return method


class CorpusReader(object):
    """
    OpenCorpora.ru corpus reader. Provides fast access to individual
    documents without loading and parsing the whole XML.
    It is capable of iterating over individual paragraphs,
    sentences and tokens without loading all data to memory.
    """

    def __init__(self, filename, cache_filename=None, use_cache=True):
        self.filename = filename
        self.use_cache = use_cache
        self._document_meta = None
        self._cache_filename = cache_filename or filename + '.~'

    def iter_documents(self, fileids=None, categories=None, _destroy=False):
        """ Return an iterator over corpus documents. """
        doc_ids = self._filter_ids(fileids, categories)
        for doc in imap(self.get_document, doc_ids):
            yield doc
            if _destroy:
                doc.destroy()

    def iter_documents_raw(self, fileids=None, categories=None):
        for doc in self.iter_documents(fileids, categories, _destroy=True):
            yield doc.raw()

    iter_paras = _from_documents('iter_paras')
    iter_raw_paras = _from_documents('iter_raw_paras')
    iter_tagged_paras = _from_documents('iter_tagged_paras')
    iter_parsed_paras = _from_documents('iter_parsed_paras')
    iter_sents = _from_documents('iter_sents')
    iter_raw_sents = _from_documents('iter_raw_sents')
    iter_tagged_sents = _from_documents('iter_tagged_sents')
    iter_parsed_sents = _from_documents('iter_parsed_sents')
    iter_words = _from_documents('iter_words')
    iter_tagged_words = _from_documents('iter_tagged_words')
    iter_parsed_words = _from_documents('iter_parsed_words')

    sents = non_iterative(iter_sents)
    raw_sents = non_iterative(iter_raw_sents)
    tagged_sents = non_iterative(iter_tagged_sents)
    parsed_sents = non_iterative(iter_parsed_sents)
    paras = non_iterative(iter_paras)
    raw_paras = non_iterative(iter_raw_paras)
    tagged_paras = non_iterative(iter_tagged_paras)
    parsed_paras = non_iterative(iter_parsed_paras)
    words = non_iterative(iter_words)
    tagged_words = non_iterative(iter_tagged_words)
    parsed_words = non_iterative(iter_parsed_words)
    documents = non_iterative(iter_documents)
    documents_raw = non_iterative(iter_documents_raw)


    def raw(self, fileids=None, categories=None):
        return "\n\n\n".join(self.iter_documents_raw(fileids, categories))

    def _doc_iterator(self, fileids, categories, doc_method):
        for doc in self.iter_documents(fileids, categories, _destroy=True):
            meth = getattr(doc, doc_method)
            for res in meth():
                yield res

    def fileids(self, categories=None):
        return list(self._filter_ids(None, categories))

    def categories(self, fileids=None, patterns=None):
        meta = self._get_meta()
        fileids = make_iterable(fileids, meta.keys())

        result = sorted(set(
            cat for cat in itertools.chain(*(
                meta[str(doc_id)].categories for doc_id in fileids
            ))
        ))

        if patterns:
            patterns = make_iterable(patterns)
            result = [cat for cat in result
                      if some_items_match([cat], patterns)]

        return result

    def catalog(self, categories=None):
        """
        Return information about documents in corpora:
        a list of tuples (doc_id, doc_title).
        """
        ids = self._filter_ids(None, categories)
        doc_meta = self._get_meta()
        return [(doc_id, doc_meta[doc_id].title) for doc_id in ids]

    def get_document(self, doc_id):
        """
        Return Document object for a given doc_id.
        This is also available as corpus[doc_id] and corpus.documents(doc_id).
        """
        return Document(self._document_xml(doc_id))

    def readme(self):
        return self.__doc__

    def get_annotation_info(self):
        for el in xml_utils.iterparse(self.filename, 'annotation', clear=True,
                                      events=('start',)):
            return {
                'version': el.get('version'),
                'revision': el.get('revision'),
            }

    def _filter_ids(self, fileids=None, categories=None):
        meta = self._get_meta()
        fileids = make_iterable(fileids, meta.keys())

        if categories is None:
            return imap(str, fileids)

        category_patterns = make_iterable(categories)
        return (doc_id for doc_id in fileids
                if some_items_match(
                    meta[doc_id].categories, category_patterns))

    def _get_meta(self):

        if self._document_meta is None and self.use_cache:
            self._load_meta_cache()

        if self._document_meta is None:
            self._document_meta = self._compute_document_meta()
            if self.use_cache:
                self._create_meta_cache()

        return self._document_meta

    def _create_meta_cache(self):
        """ Try to dump metadata to a file. """
        try:
            with open(self._cache_filename, 'wb') as f:
                compat.pickle.dump(self._document_meta, f, 1)
        except (IOError, compat.pickle.PickleError):
            pass

    def _load_meta_cache(self):
        """ Try to load metadata from file. """
        try:
            if self._should_invalidate_cache():
                os.remove(self._cache_filename)
            else:
                with open(self._cache_filename, 'rb') as f:
                    self._document_meta = compat.pickle.load(f)
        except (OSError, IOError, compat.pickle.PickleError,
                ImportError, AttributeError):
            pass

    def _should_invalidate_cache(self):
        data_mtime = os.path.getmtime(self.filename)
        cache_mtime = os.path.getmtime(self._cache_filename)
        return data_mtime > cache_mtime

    def _compute_document_meta(self):
        """
        Return documents meta information that can
        be used for fast document lookups. Meta information
        consists of documents titles, categories and positions
        in file.
        """
        meta = OrderedDict()

        bounds_iter = xml_utils.bounds(self.filename,
                            start_re=r'\s*<text id="(\d+)"[^>]*name="([^"]*)"',
                            end_re=r'\s*</text>')

        for match, bounds in bounds_iter:
            doc_id, title = str(match.group(1)), match.group(2)
            title = xml_utils.unescape_attribute(title)

            # cache categories
            xml_data = xml_utils.load_chunk(self.filename, bounds)
            doc = Document(compat.ElementTree.XML(xml_data.encode('utf8')))

            meta[doc_id] = _DocumentMeta(title, bounds, doc.categories())
        return meta

    def _document_xml(self, doc_id):
        """ Return xml Element for the document document_id. """
        doc_str = self._get_doc_by_raw_offset(str(doc_id))
        return compat.ElementTree.XML(doc_str.encode('utf8'))

    def _get_doc_by_raw_offset(self, doc_id):
        """
        Load document from xml using bytes offset information.
        XXX: this is not tested under Windows.
        """
        bounds = self._get_meta()[str(doc_id)].bounds
        return xml_utils.load_chunk(self.filename, bounds)

    def _get_doc_by_line_offset(self, doc_id):
        """
        Load document from xml using line offset information.
        This is much slower than _get_doc_by_raw_offset but should
        work everywhere.
        """
        bounds = self._get_meta()[str(doc_id)].bounds
        return xml_utils.load_chunk(self.filename, bounds, slow=True)
