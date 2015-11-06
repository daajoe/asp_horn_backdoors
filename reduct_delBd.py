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
import sys

def program_under_truth_assigment(program,backdoor):
    raise NotImplemented

def apply_del_backdoor2program(program,backdoor):
    for r in program.statements:
        r.head=list(set(r.head)-backdoor)
        r.body=list(set(r.body)-backdoor)

def is_horn(program):
    for r in program.statements:
        if r.head ==[]:
            continue
        for e in r.body:
            if e<0:
                return False
    return True
