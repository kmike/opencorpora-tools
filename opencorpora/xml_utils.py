# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import codecs
from collections import namedtuple
import re
import xml.sax.saxutils
from .compat import ElementTree

Bounds = namedtuple('Bounds', 'line_start line_end byte_start byte_end')


def iterparse(source, tag, clear=False, events=None):
    """
    iterparse variant that supports 'tag' parameter (like lxml),
    yields elements and clears nodes after parsing.
    """
    for event, elem in ElementTree.iterparse(source, events=events):
        if elem.tag == tag:
            yield elem
        if clear:
            elem.clear()


def unescape_attribute(text):
    return xml.sax.saxutils.unescape(text, {'&quot;': '"'})


def bounds(filename, start_re, end_re, encoding='utf8'):
    """
    Compute chunk bounds from text file according to start_re and end_re:
    yields (start_match, Bounds) tuples.
    """
    start_re, end_re = re.compile(start_re), re.compile(end_re)
    mo, line_start, line_end, byte_start, byte_end = [None]*5
    offset = 0

    with open(filename, 'rb') as f:
        for index, line in enumerate(f):
            line_text = line.decode(encoding)
            start_match = re.match(start_re, line_text)
            if start_match:
                mo, line_start, byte_start = start_match, index, offset

            offset += len(line)

            end_match = re.match(end_re, line_text)
            if end_match:
                yield mo, Bounds(line_start, index, byte_start, offset)
                mo, line_start, line_end, byte_start, byte_end = [None]*5


def load_chunk(filename, bounds, encoding='utf8', slow=False):
    """
    Load a chunk from file using Bounds info.
    Pass 'slow=True' for an alternative loading method based on line numbers.
    """
    if slow:
        return _load_chunk_slow(filename, bounds, encoding)

    with open(filename, 'rb') as f:
        f.seek(bounds.byte_start)
        size = bounds.byte_end - bounds.byte_start
        return f.read(size).decode(encoding)


def _load_chunk_slow(filename, bounds, encoding='utf8'):
    lines = []
    with codecs.open(filename, 'rb', encoding) as f:
        for index, line in enumerate(f):
            if index >= bounds.line_start:
                lines.append(line)
            if index >= bounds.line_end:
                break
    return ''.join(lines)


def ET_to_lxml(element):
    import lxml.etree
    return lxml.etree.fromstring(ElementTree.tostring(element))
