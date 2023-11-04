from utils import *
from pysat.card import CardEnc,EncType
from z3 import *
import networkx as nx
import random
import numpy as np
import itertools

def queen_dom_problem_exhaustive_search(n,k):
    """ exhaustive search procedure for queen domination problem

    :param n: number of rows in the chessboard
    :param k: size of the domination set
    :return: all domination set of size k for the nxn chessboard
    """
    B = np.zeros((n * n, n * n), dtype=np.bool_)
    for i in range(n * n):
        r, c = i // n, i % n
        # row
        B[i, r * n:r * n + n] = True
        # col
        B[i, c::n] = True
        # diag(s)
        D1 = [j for j in range(n * n) if r - c == ((j // n) - (j % n))]
        D2 = [j for j in range(n * n) if r + c == ((j // n) + (j % n))]
        D = D1 + D2
        B[i, D] = True

    all_solutions = [np.array(indices) + 1 for indices in itertools.combinations(list(range(n * n)), k) if np.all(np.any(B[indices, :], axis=0))]
    return all_solutions

def queen_dom_variant1_to_SAT(n,gamma,enc_type=EncType.seqcounter):
    """ A special variant of queen domination problem in which no two queens can attack each other
    """
    clauses = []
    V = [i+1 for i in range(n * n)]
    top_id = V[-1]
    for i in range(len(V)):
        N = [V[i]]
        r, c = i // n, i % n
        # squares in the same row
        N += V[r * n:r * n + n]
        # squares in the same column
        N += V[c::n]
        # squares in the same diagonal (from top left to bottom right)
        N += [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
        # squares in the same diagonal (from top right to bottom left)
        N += [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
        N = list(set(N))
        clauses.append(N)

    for i in range(n):
        # each row at most 1
        enc_row=CardEnc.atmost(lits=V[i * n:i * n + n],top_id=top_id,bound=1,encoding=enc_type)
        clauses +=enc_row.clauses
        top_id=get_top_id(clauses)
        # each column at most 1
        enc_col=CardEnc.atmost(lits=V[i::n],top_id=top_id,bound=1,encoding=enc_type)
        clauses += enc_col.clauses
        top_id=get_top_id(clauses)

    # diagonal from top left to bottom right
    d1=[[i*n+i for i in range(n)]]
    for i in range(1,n):
       d1.append([d1[i-1][j]+1 for j in range(len(d1[i-1])-1)])
    for i in range(1,n):
       d1.insert(i,[d1[i-1][j+1]-1 for j in range(len(d1[i-1])-1)])
    d1=[[V[i] for i in item] for item in d1]
    # diagonal from top right to bottom left
    d2=[[(i+1)*n-i-1 for i in range(n)]]
    for i in range(1,n):
       d2.append([d2[i-1][j]-1 for j in range(len(d2[i-1])-1)])
    for i in range(1,n):
       d2.insert(i,[d2[i-1][j+1]+1 for j in range(len(d2[i-1])-1)])
    d2=[[V[i] for i in item] for item in d2]
    # encode diagonal constraints
    for d in d1+d2:
        enc_d = CardEnc.atmost(lits=d, top_id=top_id, bound=1, encoding=EncType.seqcounter)
        clauses += enc_d.clauses
        top_id = get_top_id(clauses)

    clauses += CardEnc.equals(lits=V, top_id=top_id, bound=gamma, encoding=EncType.seqcounter).clauses
    return clauses

def queen_dom_problem_with_queen_redundancy_check_to_SAT(n,gamma):
    """ queen domination problem with queen redundancy check into SAT

    The term of redundancy is defined in the literature. Based on what they explained,
    I wrote the following formula in the first order logic. Then, I converted it into Boolean logic.

    𝑣 → ∃𝑢 ∈ 𝑁[𝑣]\{𝑣},∀𝑠 ∈ 𝑁[𝑢]\{𝑣} ~𝑠
    Note: ∀𝑡 ∈ 𝑉(𝐺),𝑡 ∈𝑁[𝑡]

    >>> solver = Solver()
    >>> formula,vertices,V= queen_dom_problem_with_queen_redundancy_check_to_SAT(3,1)
    >>> solver.add(formula)
    >>> sat= solver.check()
    >>> model = solver.model()
    >>> dominating_set = [V[i] for i in range(len(vertices)) if model[vertices[i]]]
    >>> print(dominating_set)
    [5]

    """
    V = [i + 1 for i in range(n * n)]
    G = nx.Graph()
    G.add_nodes_from(V)
    for i in range(len(V)):
        r, c = i // n, i % n
        row = V[r * n:r * n + n]
        col = V[c::n]
        D1 = [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
        D2 = [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
        G.add_edges_from([(V[i], item) for item in set(row + col + D1 + D2)])

    formula = []
    vertices = [Bool(f'{v}') for v in V]
    for v in G:
        formula.append(Or([vertices[u - 1] for u in G.neighbors(v)]))
        # Queen redundancy check
        # TODO: to be optimized further
        formula.append(Or(Not(vertices[v - 1]),
                          Or([And([Not(vertices[s - 1]) for s in G.neighbors(u) if s != v]) for u in G.neighbors(v) if
                              u != v])))
    formula.append(AtLeast(*vertices, gamma))
    formula.append(AtMost(*vertices, gamma))
    formula = And(formula)
    return formula,vertices,V

def queen_dom_MaxSAT(N=3):
    """Encodes the queen domination problem into the MaxSAT optimization problem
    >>> print(queen_dom_MaxSAT(3))
    [5]

    """
    graph = {}
    for i in range(N):
        for j in range(N):
            idx = i * N + j
            graph[idx] = [i * N + r for r in range(N) if r != j] + [r * N + j for r in range(N) if r != i]
            I, J = i - 1, j - 1
            while I >= 0 and J >= 0:
                graph[idx] += [I * N + J]
                I, J = I - 1, J - 1
            I, J = i + 1, j + 1
            while I < N and J < N:
                graph[idx] += [I * N + J]
                I, J = I + 1, J + 1
            I, J = i + 1, j - 1
            while I < N and J >= 0:
                graph[idx] += [I * N + J]
                I, J = I + 1, J - 1
            I, J = i - 1, j + 1
            while I >= 0 and J < N:
                graph[idx] += [I * N + J]
                I, J = I - 1, J + 1

    opt = Optimize()

    num_vertices = len(graph)

    vertices = [Bool(f'vertex_{i}') for i in range(num_vertices)]

    for v in range(num_vertices):
        neighbors = [vertices[v]] + [vertices[u] for u in graph[v]]
        if neighbors:
            opt.add(Or(neighbors))

    opt.minimize(Sum([If(vertices[i], 1, 0) for i in range(num_vertices)]))

    if opt.check() == sat:
        model = opt.model()
        dominating_set = [i+1 for i in range(num_vertices) if is_true(model[vertices[i]])]
        return dominating_set
    else:
        return None

def naive_isomorphism_check_networkX(n,k):
    """
    >>> print(len(naive_isomorphism_check_networkX(3,1)))
    2

    :param n: number of rows in a chessboard
    :param k: number of items to be selected from nxn squares
    :return: a list of non-isomorphism chessboards of size nxn with k queens
    """

    #TODO: to be optimized significantly

    V = [i + 1 for i in range(n * n)]
    G = nx.Graph()
    G.add_nodes_from(V)
    for v in V: G.nodes[v]['selected'] = False
    for i in range(len(V)):
        r, c = i // n, i % n
        row = V[r * n:r * n + n]
        col = V[c::n]
        D1 = [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
        D2 = [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
        G.add_edges_from([(V[i], item) for item in set(row + col + D1 + D2)])

    def inner_iso_check_helper(Gs):
        lst = []
        for g in Gs:
            for node in g.nodes:
                if g.nodes[node]["selected"] == False:
                    newG = g.copy()
                    newG.nodes[node]["selected"] = True
                    if all([True if nx.vf2pp_isomorphism(item, newG, node_label="selected") is None else False for item
                            in lst]):
                        lst.append(newG)
        return lst

    lst=[G]
    for i in range(k):
        lst=inner_iso_check_helper(lst)
    return lst

def naive_backtracking_based_on_Bird_thesis(n,desired_size):
    """ Partial, basic and inefficient implementation of the backtracking framework described in
    Computational Methods for Domination Problems by William Herbert Bird

    >>> print(naive_backtracking_based_on_Bird_thesis(3,1))
    {5}

    """
    V = [i + 1 for i in range(n * n)]
    G = nx.Graph()
    G.add_nodes_from(V)
    for i in range(len(V)):
        for i in range(len(V)):
            r, c = i // n, i % n
            row = V[r * n:r * n + n]
            col = V[c::n]
            D1 = [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
            D2 = [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
            G.add_edges_from([(V[i], item) for item in set(row + col + D1 + D2)])
    # partial set
    P = set()
    # candidate set
    C = set(V)
    # The best dominating set B found so far
    B = set(V)

    def FindDominatingSet(G, P, C, desired_size):
        nonlocal B
        if nx.is_dominating_set(G, P):
            if len(P) < len(B):
                B = P.copy()
        # if we want only one solution the below line should be existed otherwise we should remove it
        if len(B) == desired_size: return

        dominated_squares = set([n for p in P for n in G.neighbors(p)])
        q = len(dominated_squares)
        n = G.number_of_nodes()
        delta = 4 * (int(math.sqrt(n))) - 3
        k = len(P) + ((n - q) / (delta + 1))
        if k >= len(B) or k > desired_size: return
        T = set()
        undominated_squares = set(G.nodes).difference(dominated_squares)
        v = random.choice(list(undominated_squares))
        for u in set(G.neighbors(v)).intersection(C):
            T = T.union(set([u]))
            FindDominatingSet(G, P.union(set([u])), C.difference(T), desired_size)

    FindDominatingSet(G, P, C, desired_size)

    return (B if len(B)<=desired_size else None)


