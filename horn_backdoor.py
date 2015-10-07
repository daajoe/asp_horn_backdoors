#!/usr/bin/env python
#
# Copyright 2015
# Johannes K. Fichte, Vienna University of Technology, Austria
#
# horn_backdoor.py is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.  horn_backdoor.py is
# distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.  You should have received a copy of the
# GNU General Public License along with horn_backdoor.py.  If not, see
# <http://www.gnu.org/licenses/>.
#
import logging
import logging.config
logging.config.fileConfig('logging.conf')

from signal_handling import *
import contextlib
import sys
import optparse

def options():
    usage  = "usage: %prog [options] [files]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-o", "--output", dest="out", type="string", help="Output file", default=None)
    parser.add_option("-c", "--clasp", dest="clasp", action="store_true", help="Use clasp for solving", default=False)
    opts, files = parser.parse_args(sys.argv[1:])
    return opts, files

from lp_parse import *
from horn_backdoor_cplex import compute_backdoor as compute_backdoor_cplex
from horn_backdoor_clasp import compute_backdoor as compute_backdoor_clasp

@contextlib.contextmanager
def transparent_stdout(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout
    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()

def parse_and_run(f,output,clasp):
    logging.info('Parsing starts')
    p   = Parser()
    try:
        l = p.parse('x_', f)
        logging.info('Parsing done')
        logging.info('Starting ILP')
        horn_backdoor=None
        if clasp:
            horn_backdoor=compute_backdoor_clasp(l)
        else:
            horn_backdoor=compute_backdoor_cplex(l)
        logging.warning('='*80)
        logging.warning('HORN BACKDOOR'.rjust(30))
        logging.warning('='*80)
        with transparent_stdout(output) as fh:
            for e in horn_backdoor:
                fh.write('%s\n' %e)
            fh.flush()

    except IOError:
        stderr.write("error reading from: {0}\n".format(sin.filename()))
        stderr.flush()
        raise IOError


if __name__ == '__main__':
    opts,files=options()
    if sys.stdin:
        parse_and_run(sys.stdin,opts.out,opts.clasp)
    for f in files:
        parse_and_run(f,opts.out,opts.clasp)
    exit(1)


