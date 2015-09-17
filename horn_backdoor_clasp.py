from itertools import combinations,compress,imap, ifilter,izip
import logging
import logging.config
logging.config.fileConfig('logging.conf')
from copy import deepcopy
import gringo
import sys

class AnswerSet(object):
    def __init__(self):
        self.atoms=None
        self.optimization=sys.maxint

    def update_model(self,m):
        logging.warning(m.optimization()[0])
        if m.optimization()==[]:
            return
        if self.optimization > m.optimization()[0]:
            self.atoms=m.atoms()
            self.optimization=m.optimization()[0]

    def iter_edges(self):
        return imap(lambda x: x.args()[0], self.atoms)

def define_edges(l,ctl):
    logging.info('Grounding facts')
    for r in l.statements:
        neg = filter(lambda x: x<0,r.body)
        #add pairwise head
        for a1, a2 in combinations(r.head,2):
            ctl.ground([('edge',[a1,a2])])
        #add pairwise body
        for a,c in izip(ifilter(lambda x: l.symtab.tab.get(x,None),r.head),imap(lambda x: -x, neg)):
            ctl.ground([('edge',[a,c])])

def compute_backdoor(l):
    logging.info('Generate LP instance')
    ctl = gringo.Control()
    ctl.load("vc.lp")
    logging.info('Grounding rules')
    define_edges(l,ctl)
    ctl.ground([("base", [])])
    logging.info('Solving LP instance...')
    vc=AnswerSet()
    f=ctl.solve_async(on_model=vc.update_model)
    f.wait()
    logging.warning('='*80)        
    logging.warning('Solution value  = %s', vc.optimization)
    return imap(lambda x: l.symtab.tab[x], vc.iter_edges())
    

