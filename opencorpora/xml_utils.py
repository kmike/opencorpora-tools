# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import namedtuple
import re
from .compat import ElementTree

ElementBounds = namedtuple('ElementBounds', 'line_start line_end byte_start byte_end')

def iterparse(source, tag):
    """
    iterparse variant that supports 'tag' parameter (like lxml),
    handles only 'end' event, yields elements and clears nodes after parsing.
    """
    for event, elem in ElementTree.iterparse(source):
        if elem.tag == tag:
            yield elem
        elem.clear()


def bounds(filename, start_re, end_re, encoding='utf8'):
    """
    Chunks formatted xml file according to start_re and end_re:
    yields (start_match, ElementBounds) tuples.
    """
    mo, line_start, line_end, raw_start, raw_end = [None]*5
    offset = 0
    start_re, end_re = re.compile(start_re), re.compile(end_re)

    with open(filename, 'rb') as f:
        for index, line in enumerate(f):
            line_text = line.decode(encoding)
            start_match = re.match(start_re, line_text)
            if start_match:
                mo, line_start, raw_start = start_match, index, offset

            offset += len(line)

            end_match = re.match(end_re, line_text)
            if end_match:
                yield mo, ElementBounds(line_start, index, raw_start, offset)
                mo, line_start, line_end, raw_start, raw_end = [None]*5