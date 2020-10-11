=================
opencorpora-tools
=================

This package provides Python interface to http://opencorpora.org/

Install
=======

::

    pip install opencorpora-tools

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

opencorpora-tools package provides two entirely different APIs for working
with OpenCorpora XML files:

* ``opencorpora.load`` - loads XML in memory using lxml library and uses lxml
  custom Element classes to provide a nice API. Note that the full
  OpenCorpora XML corpus can take up to 10GB RAM.
* ``opencorpora.CorpusReader`` - it is slower and likely less convenient,
  but it allows to avoid loading the whole XML in memory. It also doesn't
  depend on lxml.

opencorpora.load API
--------------------

First, load corpus to memory:

    >>> import opencorpora
    >>> corpus = opencorpora.load('annot.opcorpora.xml')
    >>> corpus
    <Corpus revision=4213997 docs:3489 tokens:1740169>
    >>> corpus.revision
    '4213997'
    >>> corpus.version
    '0.12'

Access documents:

    >>> len(corpus.docs)
    3489
    >>> corpus.docs[42]
    <Doc id=44 tokens:2502 name='18801 Хитрость духа'>
    >>> corpus[42]   # it is the same as corpus.docs[42]
    <Doc id=44 tokens:2502 name='18801 Хитрость духа'>

Sentences, paragraphs and tokens can be accessed directly:

    >>> corpus.sentences[0]
    <Sentence id=1 source='«Школа злословия» учит прикусить язык'>
    >>> corpus.paragraphs[0]
    <Paragraph id=1 source='«Школа злословия» учит прикусить язык  Сохранится ли градус дискуссии в новом сезоне?'>
    >>> len(corpus.tokens)
    1740169

Work with Doc objects:

    >>> doc = corpus[42]
    >>> doc
    <Doc id=44 tokens:2502 name='18801 Хитрость духа'>
    >>> doc.id
    '44'
    >>> doc.name
    '18801 Хитрость духа'
    >>> doc.source
    'Хитрость духа  Почему князь Владимир крестил Русь\n\n28 июля православная ...'
    >>> doc.tags
    ['Автор:Олег Давыдов', 'Год:2010', 'Дата:28/07', 'url:http://www.chaskor.ru/article/28_iyulyahitrost_duha_18801', 'Тема:ЧасКор:Общество']
    >>> doc.paragraphs
    [<Paragraph id=1176 source='Хитрость духа  Почему князь Владимир крестил Русь'>, ...]
    >>> doc.sentences
    [<Sentence id=3433 source='Хитрость духа'>,
     <Sentence id=3434 source='Почему князь Владимир крестил Русь'>,
     ...
    ]
    >>> doc.tokens
    [<Token id=64838 source='Хитрость'>, <Token id=64839 source='духа'>, ...]
    >>> doc[0]  # the same as doc.tokens[0]
    <Token id=64838 source='Хитрость'>

Paragraph objects:

    >>> para = doc.paragraphs[0]
    >>> para.id
    '1176'
    >>> para.source
    'Хитрость духа  Почему князь Владимир крестил Русь'
    >>> para.sentences
    [<Sentence id=3433 source='Хитрость духа'>, <Sentence id=3434 source='Почему князь Владимир крестил Русь'>]
    >>> para.tokens
    [<Token id=64838 source='Хитрость'>, <Token id=64839 source='духа'>, ...]
    >>> para[0]  # the same as para.tokens[0]
    <Token id=64838 source='Хитрость'>

Sentence objects:

    >>> sent = doc.sentences[6]
    >>> sent
    <Sentence id=3439 source='У князя Святослава Игоревича было три сына: Ярополк, Олег и Владимир.'>
    >>> sent.id
    '3439'
    >>> sent.source
    'У князя Святослава Игоревича было три сына: Ярополк, Олег и Владимир.'
    >>> sent.tokens
    [<Token id=64912 source='У'>, <Token id=64913 source='князя'>, <Token id=64914 source='Святослава'>, ...]
    >>> sent[1]  # the same as sent.tokens[1]
    <Token id=64913 source='князя'>

Token objects:

    >>> token = sent[1]
    >>> token
    <Token id=64913 source='князя'>
    >>> token.id
    '64913'
    >>> token.source
    'князя'
    >>> token.parses
    [<Parse id=134923 lemma=князь grammemes=['NOUN', 'anim', 'masc', 'sing', 'gent']>,
     <Parse id=134923 lemma=князь grammemes=['NOUN', 'anim', 'masc', 'sing', 'accs']>]
    >>> token.lemma  # lemma of a first parse, the same as token.parses[0].lemma
    'князь'
    >>> token.grammemes  # the same as token.parses[0].grammemes
    ['NOUN', 'anim', 'masc', 'sing', 'gent']
    >>> token.parse  # the same as token.parses[0]
    <Parse id=134923 lemma=князь grammemes=['NOUN', 'anim', 'masc', 'sing', 'gent']>

Corpus, Doc, Paragraph, Sentence, Token and Parse are custom etree Element
subclasses. You're not limited to the API described above - e.g. it is possible
to process corpus using XPath expressions, and lxml will return
these custom Element classes in results if a tree is loaded using
``opencorpora.load``.

opencorpora.CorpusReader API
----------------------------

Initialize::

    >>> import opencorpora
    >>> corpus = opencorpora.CorpusReader('annot.opcorpora.xml')

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
get an idea how to work with the API. It it not exactly the same,
but should be very similar.

Currently CorposReader doesn't provide a way to access original OpenCorpora
ids of paragraphs/sentences/tokens.


Performance
===========

OpenCorpora XML is huge (>250MB) so building full DOM tree requires
a lot of memory (several GB, it coud be 10GB+ for full corpus).
If RAM is not an issue ``opencorpora.load`` should be faster and
more convenient; otherwise ``opencorpora.CorpusReader`` should work better.

``opencorpora.CorpusReader`` handles it this way:

1. ``corpus.get_document(doc_id)`` or ``corpus.documents(doc_ids)``
   don't load the original XML to memory and don't parse the whole XML.
   They use precomputed offset information to slice the XML instead.
   The offset information is computed on first access and
   saved to "<name>.~" file.

   Consider document loading O(1) regarding full XML size.
   Individual documents are not huge so they and loaded and parsed as usual.

2. There are iterator methods for all corpora API (``corpus.iter_words``, etc).


Development
===========

Development happens at github: https://github.com/kmike/opencorpora-tools
Issue tracker: https://github.com/kmike/opencorpora-tools/issues.
Feel free to submit ideas, bugs or pull requests.

Running tests
-------------

Make sure `tox <http://tox.testrun.org>`_ is installed and run

::

    $ tox

from the source checkout. Tests should pass under Python 2.7 and 3.5+.
