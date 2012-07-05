=================
opencorpora-tools
=================

This package provides Python interface to http://opencorpora.org/

Installation
============

::

    pip install opencorpora-tools

If you have python 2.6 then argparse and ordereddict packages are required::

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

Get table of contents::

    >>> corpus.catalog()
    [('1', '"Частный корреспондент"'),
     ('2', '00021 Школа злословия'),
     ('3', '00022 Последнее восстание в Сеуле'),
     ('4', '00023 За кота - ответишь!'),
    ...

Work with documents::

    >>> seoul_words = corpus.words('3')
    >>> seoul_words
    ['«', 'Последнее', 'восстание', '»', 'в', 'Сеуле', ...

    >>> corpus.documents(categories='Тема:ЧасКор:Книги*')
    [Document: 21759 2001-2010-й: книги, которые потрясали,
     Document: 12824 86 снов, вызванных полётом пчелы вокруг граната за секунду до пробуждения,
     Document: 10930 А бойтесь единственно только того, кто скажет: «Я знаю, как надо!»,
     ...

``opencorpora.Corpora`` is modelled after NLTK's CorpusReader interface;
consult with http://nltk.googlecode.com/svn/trunk/doc/book/ch02.html to
get an idea how to work with the API.

It it not exactly the same, but is very similar. E.g. ``sents()`` in
opencorpora-tools returns a list of ``Sentence`` instances and ``sents()``
in NLTK returns a list of list of strings, but ``Sentence`` instances quacks
like a list of strings (it can be indexed, iterated, etc.).


Performance
===========

OpenCorpora XML is huge (>250MB) so building full DOM tree requires
a lot of memory (several GB) and should be avoided.

opencorpora-tools handles it this way:

1. ``corpus[doc_id]`` or ``corpus.get_document(doc_id)`` or
   ``corpus.documents(doc_ids)`` don't load the original
   XML to memory and don't parse it. They use precomputed offset
   information to slice the XML instead. The offset information is computed
   on first access and saved to "<name>.~" file.

   Consider document loading O(1) regarding XML size. Individual documents
   are not huge so they and loaded and parsed as usual.

2. There are iterator methods for all corpora API (``corpus.iterwords``, etc).


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

from the source checkout. Tests should pass under python 2.6..3.2
and pypy > 1.8.