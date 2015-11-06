#!/usr/bin/env python
#
# Copyright 2015
# Johannes K. Fichte, Vienna University of Technology, Austria
#
# reduct.py is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.  reduct.py is distributed in the
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with reduct.py.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
import logging.config
logging.config.fileConfig('logging.conf')

from signal_handling import *
import contextlib
import sys
import optparse

def options():
    usage  = "usage: %prog [options] [backdoor]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-o", "--output", dest="out", type="string", help="Output file", default=None)
    parser.add_option("-c", "--clasp", dest="clasp", action="store_true", help="Use clasp for solving", default=False)
    parser.add_option("--horn", dest="horn", action="store_true", help="Check for Horn backdoor", default=False)
    parser.add_option('-x', '--use_predicate', dest="use_predicate", action="store_true", help='Backdoor atoms stored in predicate "_backdoor(X)"', default=False)
    opts, bd_files = parser.parse_args(sys.argv[1:])
    if len(bd_files)<1:
        raise TypeError('No backdoor given')
    if len(bd_files)>1:
        raise TypeError('More than one backdoor given.')
    return opts, bd_files[0]

from lp_parse import *
from reduct_delBd import *


def read_backdoor_ids_from_file(bd_file_name,l,use_predicate):
    atoms={}
    for k,v in l.symtab.tab.iteritems():
        atoms[v] = k

    import re
    regex = re.compile(r'_backdoor\(([\w,\(\)]+)\).')

    backdoor = set([])
    with open(bd_file_name, 'r') as f:
        for line in f.readlines():
            line=line.rstrip('\n\r')
            if use_predicate:
                pred=re.findall(regex,line)
                if len(pred)!=1:
                    raise ValueError('_backdoor(..) not found in line')
                line=pred[0]
            try:
                value=atoms[line]
            except KeyError, e:
                value=line[2:]
            backdoor.add(int(value))
            backdoor.add(-int(value))
    return backdoor


def parse_and_run(f,bd_file_name,output,clasp,horn,use_predicate):
    logging.info('Parsing starts')
    p   = Parser()
    try:
        l = p.parse('x_', f)
        logging.info('Parsing done')
        logging.info('Reading Backdoor')
        
        backdoor=read_backdoor_ids_from_file(bd_file_name,l,use_predicate)
        logging.info('Applying Backdoor')
        apply_del_backdoor2program(l,backdoor)
        if horn:
            exit(is_horn(l))
        else:
            l.write(sys.stdout)

    except IOError:
        stderr.write("error reading from: {0}\n".format(sin.filename()))
        stderr.flush()
        raise IOError


if __name__ == '__main__':
    opts,files=options()
    if sys.stdin:
        parse_and_run(sys.stdin,files,opts.out,opts.clasp,opts.horn,opts.use_predicate)
    else:
        raise RuntimeError('No stdin')
    exit(1)


