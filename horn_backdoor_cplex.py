from itertools import combinations,compress,imap, ifilter,izip
import logging
import logging.config
logging.config.fileConfig('logging.conf')

import cplex
from cplex.exceptions import CplexError

def add_vars(l,ilp):
    lb=[0.0]*len(l.symtab.tab.keys())
    ub=[1.0]*len(l.symtab.tab.keys())
    obj=[1.0]*len(l.symtab.tab.keys())
    types=["B"] * len(l.symtab.tab.keys())
    ilp.variables.add(obj=obj,types=types, names=map(str,l.symtab.tab.keys()))
    
def add_edge_constraint(l,ilp,v1,v2):
    logging.debug('%s-%s', l.symtab.tab.get(v1,None),l.symtab.tab.get(v2,None))
    vars = map(str,[v1,v2])
    
    if not l.symtab.tab.get(v1,None):
        ilp.variables.add(obj=[1.0],types=["B"], names=map(str,[v1]))
    if not l.symtab.tab.get(v2,None):
        ilp.variables.add(obj=[1.0],types=["B"], names=map(str,[v2]))

    ilp.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = vars, val = [1, 1])],
                               senses='G', 
                               rhs = [1],
                               names=['e(%s,%s)'%tuple(vars)])

def define_ilp(l):
    ilp = cplex.Cplex()
    add_vars(l,ilp)
    ilp.objective.set_sense(ilp.objective.sense.minimize)

    for r in l.statements:
        neg = filter(lambda x: x<0,r.body)
        #add pairwise head
        for a1, a2 in combinations(r.head,2):
            add_edge_constraint(l,ilp,a1,a2)
        #add pairwise body
        for a,c in izip(ifilter(lambda x: l.symtab.tab.get(x,None),r.head),imap(lambda x: -x, neg)):
            add_edge_constraint(l,ilp,a,c)
    return ilp


def compute_backdoor(l):
    try:
        logging.info('Generate ILP instance')
        ilp=define_ilp(l)
        logging.info('Solving ILP instance...')
        #ilp.parameters.threads.set(1)
        ilp.solve()
        logging.info('Instance solved.')
        logging.info(ilp.solution.get_status())
        logging.info(ilp.solution.status[ilp.solution.get_status()])
        logging.warning('='*80)        
        logging.warning('Solution value  = %s', ilp.solution.get_objective_value())
        return compress(imap(lambda x: l.symtab[int(x)],ilp.variables.get_names()),ilp.solution.get_values())
    except CplexError, e:
        logging.error(e)
        return
