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
    return set(l.symtab.tab.keys())
    
def add_var(v,ilp,cplex_vars):
    if v not in cplex_vars:
        ilp.variables.add(obj=[1.0],types=['B'], names=[v])
        cplex_vars.add(v)

def add_unnamed_symbols(v,l,ilp,cplex_vars):
    if not l.symtab.tab.get(v,None):
        add_var(l.symtab[v][2:],ilp,cplex_vars)

def add_edge_constraint(l,ilp,cplex_vars,v1,v2):
    logging.debug('%s-%s', l.symtab[v1],l.symtab[v2])
    vars_ = map(str,[v1,v2])
    map(lambda x: add_unnamed_symbols(x,l,ilp,cplex_vars), vars_)
    ilp.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = vars_, val = [1, 1])],
                               senses='G', 
                               rhs = [1],
                               names=['e(%s,%s)'%tuple(vars_)])

def define_ilp(l):
    ilp = cplex.Cplex()
    cplex_vars=add_vars(l,ilp)
    ilp.objective.set_sense(ilp.objective.sense.minimize)

    for r in l.statements:
        #add pairwise head
        for a1, a2 in combinations(r.head,2):
            add_edge_constraint(l,ilp,cplex_vars,a1,a2)
        #add pairwise body
        for a in ifilter(lambda x: l.symtab[x],r.head):
            neg = filter(lambda x: x<0,r.body)
            for c in imap(lambda x: -x, neg):
                add_edge_constraint(l,ilp,cplex_vars,a,c)
    return ilp


def compute_backdoor(l,threads):
    try:
        logging.info('Generate ILP instance')
        ilp=define_ilp(l)
        logging.info('Solving ILP instance...')
        if threads:
            ilp.parameters.threads.set(threads)
        ilp.solve()
        logging.info('Instance solved.')
        logging.info('Status = %n', ilp.solution.get_status())
        logging.info(ilp.solution.status[ilp.solution.get_status()])
        logging.warning('='*80)        
        logging.warning('Solution value  = %s', ilp.solution.get_objective_value())
        return compress(imap(lambda x: l.symtab[int(x)],ilp.variables.get_names()),ilp.solution.get_values())
    except CplexError, e:
        logging.error(e)
        return
