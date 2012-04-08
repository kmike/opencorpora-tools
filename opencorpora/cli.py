#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import sys
import bz2
import argparse
import urllib2

CORPORA_URL_BZ2 = 'http://opencorpora.org/files/export/annot/annot.opcorpora.xml.bz2'
DEFAULT_OUT_FILE = 'annot.opcorpora.xml.bz2'
CHUNK_SIZE = 256*1024

parser = argparse.ArgumentParser(
    description='opencorpora.org interface',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
subparsers = parser.add_subparsers()

parser_download = subparsers.add_parser('download',
    help='download and decompress annotated XML corpora',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser_download.add_argument('-o', '--output', type=str, help='destination file', default=DEFAULT_OUT_FILE)
parser_download.add_argument('--url', help='download url', default=CORPORA_URL_BZ2)
parser_download.add_argument('--decompress',  help='decompress', action='store_true')

def download(args):
    decompressor = bz2.BZ2Decompressor()
    out_file = args.output
    if args.decompress and out_file == DEFAULT_OUT_FILE:
        out_file = DEFAULT_OUT_FILE[:-4]

    print('Connecting...')
    fp = urllib2.urlopen(args.url, timeout=30)

    print('Creating %s from %s' % (out_file, args.url))
    with open(out_file, 'w') as out:
        while 1:
            data = fp.read(CHUNK_SIZE)
            if not data:
                break

            if args.decompress:
                out.write(decompressor.decompress(data))
            else:
                out.write(data)

            sys.stdout.write('.')
            sys.stdout.flush()

    print('\nDone.')

parser_download.set_defaults(func=download)

def main():
    args = parser.parse_args()
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())