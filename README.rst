=================
opencorpora-tools
=================

This package provides Python interface to http://opencorpora.org/

Installation
============

::

    pip install opencorpora-tools

If you have python < 2.7 then argparse and ordereddict packages are required::

    pip install argparse
    pip install ordereddict

Usage
=====

Obtaining corpora
-----------------

Opencorpora-tools works with XML from http://opencorpora.org/.

You can download and unpack the XML manually (from 'Downloads' page) or
just use the provided command-line util::

    $ opencorpora download

Run ``opencorpora download --help`` for more options.

Using corpora
-------------

Initialize::

    >>> import opencorpora
    >>> corpus = opencorpora.Corpora('annot.opcorpora.xml')

Get a list of documents::

    >>> catalog = corpus.catalog()
    >>> doc_id, doc_title = catalog[1590]
    >>> print doc_id
    1610

    >>> doc_title
    24105 Герман Греф советует россиянам «не суетиться» с валютой

Work with a document::

    >>> doc = corpus[1610]
    >>> print doc.title()
    24105 Герман Греф советует россиянам «не суетиться» с валютой

    >>> print doc.words()[11]
    Сбербанка

    >>> doc.sents()[0]
    <class 'opencorpora.Sentence'>: Герман Греф советует россиянам «не суетиться» с валютой

    >>> print doc.paras()[0]
    Герман Греф советует россиянам «не суетиться» с валютой Президент Сбербанка уверен, что в ближайшее время на валютных рынках сохранится высокая волатильность и «шараханье».



``Corpora``, ``Document``, ``Paragraph`` and ``Sentence`` classes support
the following methods (when it make sense, e.g. sentence doesn't have paragraphs):

* ``words()`` - returns a list of words and other tokens;
* ``sents()`` - returns a list of ``Sentence`` instances;
* ``paras()`` - returns a list of ``Paragraph`` instances;
* ``documents()`` - returns a list of ``Document`` instances (this is memory hog!);
* ``tagged_words()`` - returns a list of (str, str);
* ``tagged_sents()`` - returns a list of (list of (str, str));
* ``tagged_paras()`` - returns a list of (list of (list of (str, str)));
* ``iterwords()``, ``itersents()``, ``iterparas()``, ``iterdocuments()``,
  ``iter_tagged_words``, ``iter_tagged_sents``, ``iter_tagged_paras`` - return
  iterators over words, sentences, paragraphs or documents;

You can also iterate over ``Corpora``, ``Document``, ``Paragraph`` and ``Sentence``
(this yields documents, paragraphs, sentences and words), e.g.::

    >>> sent = doc.sents()[0]
    >>> for word in sent:
    ...     print word
    ...
    Герман
    Греф
    советует
    россиянам
    «
    не
    суетиться
    »
    с
    валютой


The API is modelled after NLTK's CorpusReader API.

It it not exactly the same, but is very similar. E.g. ``sents()`` in
opencorpora-tools returns a list of ``Sentence`` instances and ``sents()``
in NLTK returns a list of list of strings, but ``Sentence`` instances quacks
like a list of strings (it can be indexed, iterated, etc.) so
``opencorpora.Corpora`` API may be seen as a superset of NLTK CorpusReader API.


Performance
===========

OpenCorpora XML is huge (>250MB) so building full DOM tree requires
a lot of memory (several GB) and should be avoided.

opencorpora-tools handles it this way:

1. ``corpus[doc_id]`` or ``corpus.get_document(doc_id)`` don't load
   the original XML to memory and don't parse it. They use precomputed offset
   information to slice the XML instead. The offset information is computed
   on first access and saved to "<name>.~" file.

   Consider document loading O(1) regarding XML size. Individual documents
   are not huge so they and loaded and parsed as usual.

2. There are iterator methods for all corpora API.


Development
===========

Development happens at github and bitbucket:

* https://github.com/kmike/opencorpora-tools
* https://bitbucket.org/kmike/opencorpora-tools

The main issue tracker is at github.

Feel free to submit ideas, bugs, pull requests (git or hg) or regular patches.

Running tests
-------------

Make sure `tox <http://tox.testrun.org>`_ is installed and run

::

    $ tox

from the source checkout. Tests should pass under python 2.6..3.2 and pypy > 1.8.