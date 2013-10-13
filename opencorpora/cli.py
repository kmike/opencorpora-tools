#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import sys
import bz2
import argparse
from opencorpora.compat import urlopen

FULL_CORPORA_URL_BZ2 = 'http://opencorpora.org/files/export/annot/annot.opcorpora.xml.bz2'
DISAMBIGUATED_CORPORA_URL_BZ2 = 'http://opencorpora.org/files/export/annot/annot.opcorpora.no_ambig.xml.bz2'
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
parser_download.add_argument('-d', '--disambig', help='download disambiguated corpora', action='store_true')
parser_download.add_argument('--url', help='download url', default=FULL_CORPORA_URL_BZ2)
parser_download.add_argument('--no-decompress',  help='do not decompress data', action='store_true')
parser_download.add_argument('-q', '--quiet', help='be less noisy', action='store_true')


def _download_file(url, out_fp, decompress=True, chunk_size=CHUNK_SIZE, on_chunk=lambda:None):
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


def _download(out_file, decompress, disambig, url, verbose=True):
    if decompress and out_file == DEFAULT_OUT_FILE:
        out_file = DEFAULT_OUT_FILE[:-4]

    if disambig:
        url = DISAMBIGUATED_CORPORA_URL_BZ2

    if verbose:
        print('Creating %s from %s' % (out_file, url))

    with open(out_file, 'wb') as out:
        if verbose:
            def on_chunk():
                sys.stdout.write('.')
                sys.stdout.flush()
        else:
            on_chunk = lambda: None
        _download_file(url, out, decompress, on_chunk=on_chunk)

    if verbose:
        print('\nDone.')


def download(args):
    _download(args.output, not args.no_decompress, args.disambig, args.url, not args.quiet)
parser_download.set_defaults(func=download)


def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
