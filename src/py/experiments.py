from pysat.solvers import Solver
from problems import *
from utils import *
import datetime

def exp_1(n,gamma,sat_solver='maplesat',plot=False,verbose=True):
    """
    >>> exp_1(3,1,plot=False,verbose=False)
    ([5], None)

    :param n: number of rows in a nxn chessboard
    :param gamma: size of the domination set
    :param sat_solver: SAT solver's name
    :param plot: if True, it will plot the domination set graphically
    :param verbose: if True, it will print reporting messages
    :return: domination set, and proof such that one of these two would be None
    """
    start_time = datetime.datetime.now()
    if verbose:print("started")
    dominating_set,proof = None,None
    with Solver(bootstrap_with=queen_dom_to_SAT(n, gamma), name=sat_solver) as s:
        if s.solve():
            dominating_set = [item for item in s.get_model() if item in range(1, n * n + 1)]
            if verbose:print('indices are started from 1:', dominating_set)
        else:
            try:
                proof=s.get_proof()
                if verbose: print(proof)
            except Exception as e:
                if verbose: print(e)

    end_time = datetime.datetime.now()
    if verbose:print(f"finished: {end_time - start_time}")
    if plot and dominating_set is not None:
        display_chessboard([['Q' if (i * n + j + 1) in dominating_set else '' for j in range(n)] for i in range(n)])

    return dominating_set,proof

