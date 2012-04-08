# -*- coding: utf-8 -*-
from __future__ import absolute_import

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict