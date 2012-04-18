#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import sys
import bz2
import argparse
from opencorpora.compat import urlopen

CORPORA_URL_BZ2 = 'http://opencorpora.org/files/export/annot/annot.opcorpora.xml.bz2'
DEFAULT_OUT_FILE = 'annot.opcorpora.xml.bz2'
CHUNK_SIZE = 256*1024

parser = argparse.ArgumentParser(
    description='opencorpora.org interface',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
subparsers = parser.add_subparsers()

parser_download = subparsers.add_parser('download',
    help='download and (optionally) decompress annotated XML corpora',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser_download.add_argument('-o', '--output', type=str, help='destination file', default=DEFAULT_OUT_FILE)
parser_download.add_argument('--url', help='download url', default=CORPORA_URL_BZ2)
parser_download.add_argument('--no-decompress',  help='do not decompress data', action='store_true')

def _download(url, out_fp, decompress=True, chunk_size=CHUNK_SIZE, on_chunk=lambda:None):
    decompressor = bz2.BZ2Decompressor()
    fp = urlopen(url, timeout=30)

    while 1:
        data = fp.read(chunk_size)
        if not data:
            break

        if decompress:
            out_fp.write(decompressor.decompress(data))
        else:
            out_fp.write(data)
        on_chunk()

def download(args):
    out_file = args.output
    decompress = not args.no_decompress
    if decompress and out_file == DEFAULT_OUT_FILE:
        out_file = DEFAULT_OUT_FILE[:-4]

    print('Creating %s from %s' % (out_file, args.url))

    with open(out_file, 'w') as out:
        def on_chunk():
            sys.stdout.write('.')
            sys.stdout.flush()

        _download(args.url, out, decompress, on_chunk=on_chunk)

    print('\nDone.')

parser_download.set_defaults(func=download)

def main():
    args = parser.parse_args()
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())