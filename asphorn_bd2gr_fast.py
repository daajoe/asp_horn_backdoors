#!/usr/bin/env python2
#
# Copyright 2018
# Johannes K. Fichte, TU Dresden, Germany
#
# horn_bd2gr.py is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.  horn_bd2gr.py is
# distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.  You should have received a copy of the
# GNU General Public License along with horn_bd2gr.py.  If not, see
# <http://www.gnu.org/licenses/>.
#
import gzip
import mimetypes
import os
from bz2 import BZ2File

from cStringIO import StringIO

# from tempfile import NamedTemporaryFile

__license__ = 'GPL'
__version__ = '0.0.1'

import argparse
import logging
import logging.config
from itertools import combinations, ifilter, izip, imap
import signal

from lp_parse import *

logging.config.fileConfig('logging.conf')


# noinspection PyUnusedLocal
def signal_handler(sig, frame):
    logging.warning('Received external Interrupt signal. Solvers will stop and save data')
    logging.warning('Exiting.')
    exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def is_valid_file(parser, arg):
    if not arg:
        parser.error('Missing file.')
    if not os.path.exists(arg):
        parser.error('The file "%s" does not exist!' % arg)


def parse_args():
    parser = argparse.ArgumentParser(description='%(prog)s -instance instance')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))

    root_group = parser.add_mutually_exclusive_group()
    root_group.add_argument('-f', '--file', dest='instance', action='store', type=lambda x: os.path.realpath(x),
                            help='instance')
    args = parser.parse_args()
    is_valid_file(parser, args.instance)
    return args


def define_edges(l, stream):
    logging.info('Generating Edges')
    num_edges = 0
    s = SymTab()
    for r in l.statements:
        neg = filter(lambda x: x < 0, r.body)
        # add pairwise head
        for a1, a2 in combinations(r.head, 2):
            assert (a1 != a2)
            assert (s.atom_id(a1) != s.atom_id(a2))
            stream.write("%s %s\n" % (s.atom_id(a1), s.atom_id(a2)))
            num_edges += 1
        # add pairwise body
        for a, c in izip(ifilter(lambda x: l.symtab.tab.get(x, None), r.head), imap(lambda x: -x, neg)):
            assert (a != c)
            assert (s.atom_id(a) != s.atom_id(c))
            stream.write("%s %s\n" % (s.atom_id(a), s.atom_id(c)))
            num_edges += 1
    return s.last_atom, num_edges


try:
    import backports.lzma as xz

    xz = True
except ImportError:
    xz = False


def transparent_compression(filename):
    m_type = mimetypes.guess_type(filename)[1]
    if m_type is None:
        stream = open(filename, 'r')
    elif m_type == 'bzip2':
        stream = BZ2File(filename, 'r')
    elif m_type == 'gz' or m_type == 'gzip':
        stream = gzip.open(filename, 'r')
    elif m_type == 'xz' and xz:
        stream = xz.open(filename, 'r')
    else:
        raise IOError('Unknown input type "%s" for file "%s"' % (m_type, filename))
    return stream


class SymTab(object):
    symtab = {}
    last_atom = 0

    def atom_id(self, atom_name):
        if self.symtab.has_key(atom_name):
            return self.symtab[atom_name]
        else:
            self.last_atom += 1
            self.symtab[atom_name] = self.last_atom
            return self.last_atom


def asp_parse_and_gen_graph(in_stream):
    logging.info('Parsing starts...')
    try:
        p = Parser()
        l = p.parse('x_', in_stream)
        logging.info('Parsing done')
        out_stream = StringIO()
        num_verts, num_edges = define_edges(l, out_stream)
        return {'stream': out_stream, 'num_verts': num_verts, 'num_edges': num_edges}

    except IOError:
        sys.stderr.write("Error reading from: {0}\n".format(in_stream.filename()))
        sys.stderr.flush()
        raise IOError


def write_graph(ostream, num_verts, num_edges, stream):
    ostream.write("p td %s %s\n" % (num_verts, num_edges))
    ostream.write(stream.getvalue())
    ostream.flush()


if __name__ == '__main__':
    args = parse_args()
    instance = args.instance
    # output_instance = "%s.gr.bz2" % instance
    output_instance = "%s.gr" % instance

    sin = fileinput.input(instance)
    ret = asp_parse_and_gen_graph(sin)

    ostream = StringIO()
    write_graph(ostream=ostream, num_verts=ret['num_verts'],
                num_edges=ret['num_edges'], stream=ret['stream'])
    with open(output_instance, 'w') as fh:
        fh.write(ostream.getvalue())
    # print ostream.getvalue()
    # tarbz2contents = bz2.compress(ostream.getvalue(), 9)
    #
    # with open(output_instance, 'wb') as fh:
    #     fh.write(tarbz2contents)

    #
    exit(0)
