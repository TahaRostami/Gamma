import datetime
import networkx as nx
import math
import random
from multiprocessing import Pool
import os
import pandas as pd

def Algorithm32(args):
    n, desired_size, bounding_strategy_enb = args

    def _find_dominating_set(P,NP,size_of_NP,desired_size,i):
        nonlocal self_G
        nonlocal self_C
        nonlocal self_B
        nonlocal num_all_call

        num_all_call+=1

        # |V (G)|
        n=len(self_G)
        if size_of_NP==n:
            if len(P)<len(self_B):
                self_B=P.copy()
            return

        while i<len(NP) and NP[i]:
            i+=1

        k= len(P)
        if bounding_strategy_enb==1:
            k+=(n-size_of_NP)//(self_delta+1)
        if k>=len(self_B) or k>desired_size:
            return
        #Empty stack
        F=[]
        #{Try vertex vi, if applicable
        if self_C[i]:
            #Remove vi from C
            self_C[i]=False
            #Update data
            new_P=P + [i]
            new_NP=NP.copy()
            new_size_of_NP=size_of_NP
            for j in self_G[i]:
                if new_NP[j]==False:
                    new_NP[j]=True
                    new_size_of_NP+=1
            _find_dominating_set(new_P,new_NP,new_size_of_NP,desired_size,i+1)
            #Push i onto F
            F.append(i)
        #Try undominated neighbours of vi
        for vj in self_G[i]:
            if self_C[vj] and i!=vj and NP[vj]==False:
                # Remove vj from C
                self_C[vj] = False
                # Update data
                new_P = P + [vj]
                new_NP = NP.copy()
                new_size_of_NP = size_of_NP
                for w in self_G[vj]:
                    if new_NP[w] == False:
                        new_NP[w] = True
                        new_size_of_NP += 1
                _find_dominating_set(new_P, new_NP, new_size_of_NP, desired_size, i + 1)
                # Push j onto F
                F.append(vj)

        #Try dominated neighbours of vi
        for vj in self_G[i]:
            if self_C[vj] and i!=vj and NP[vj]:
                # Remove vj from C
                self_C[vj] = False
                # Update data
                new_P = P + [vj]
                new_NP = NP.copy()
                new_size_of_NP = size_of_NP
                for w in self_G[vj]:
                    if new_NP[w] == False:
                        new_NP[w] = True
                        new_size_of_NP += 1
                _find_dominating_set(new_P, new_NP, new_size_of_NP, desired_size, i + 1)
                # Push j onto F
                F.append(vj)

        while len(F)>0:
            j=F.pop()
            self_C[j]=True

    def get_adj_lst(n):
        B = []
        V = [i for i in range(n * n)]
        for i in range(n * n):
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
            B.append(N)
        return B

    num_all_call=0
    # G: adj list representation of the graph
    self_G=get_adj_lst(n)
    # ∆: computing maximum degree of the graph G
    self_delta = max([len(v) for v in self_G])
    # The partial dominating set P is represented by array-based list
    P = []
    # The best known dominating set is represented by array-based list
    self_B = list(range(len(self_G)))
    # NP: The set N[P] which contains all dominated vertices
    NP = [False] * len(self_G)
    #: |N[P]|
    size_of_NP = 0
    # C: The set of candidate vertices
    self_C = [True] * len(self_G)
    # To decide if G has a dominating set of size at most desired_size
    desired_size = len(self_G) if desired_size is None else desired_size
    # The initial call
    start_time = datetime.datetime.now()
    _find_dominating_set(P, NP, size_of_NP, desired_size, 0)
    end_time = datetime.datetime.now()
    # For numbering consistency
    self_B=[item+1 for item in self_B]

    print(Algorithm32.__name__,n, desired_size, bounding_strategy_enb,num_all_call,(end_time - start_time).seconds)
    return self_B,num_all_call,(end_time - start_time)
def naive_backtracking_based_on_Bird_thesis(args):
    n, desired_size, bounding_strategy_enb=args
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

    num_calls=0

    def FindDominatingSet(G, P, C, desired_size):
        nonlocal B
        nonlocal bounding_strategy_enb
        nonlocal num_calls

        num_calls+=1

        if nx.is_dominating_set(G, P):
            if len(P) < len(B):
                B = P.copy()
            return

        dominated_squares = set([n for p in P for n in G.neighbors(p)])
        undominated_squares = set(G.nodes).difference(dominated_squares)
        if bounding_strategy_enb==2:
           U=sorted([G.degree[item] for item in undominated_squares],reverse=True)
           x=0
           t=0
           while x<len(undominated_squares):
               x+=U[t]
               t+=1
        k = len(P)
        if bounding_strategy_enb==1:
            q = len(dominated_squares)
            n = G.number_of_nodes()
            delta = 4 * (int(math.sqrt(n))) - 3
            k += ((n - q) / (delta + 1))
        elif bounding_strategy_enb==2:
            k += t

        if k >= len(B) or k > desired_size: return

        T = set()

        v = random.choice(list(undominated_squares))
        for u in set(G.neighbors(v)).intersection(C):
            T = T.union(set([u]))
            FindDominatingSet(G, P.union(set([u])), C.difference(T), desired_size)

    start_time = datetime.datetime.now()
    FindDominatingSet(G, P, C, desired_size)
    end_time = datetime.datetime.now()

    print(naive_backtracking_based_on_Bird_thesis.__name__, n, desired_size, bounding_strategy_enb, num_calls, (end_time - start_time).seconds)
    return (B if len(B)<=desired_size else None),num_calls,(end_time - start_time)


if __name__=='__main__':

    # configs=[{'algo':naive_backtracking_based_on_Bird_thesis,'params':[(8,4,0),(8,4,1),(8,5,0),(8,5,1),(9,4,0),(9,4,1),(9,5,0),(9,5,1),(10,4,0),(10,4,1),(10,5,0),(10,5,1),(11,4,0),(11,4,1),(11,5,0),(11,5,1),(12,5,0),(12,5,1),(12,6,0),(12,6,1)],'results':[]},
    #  {'algo': naive_backtracking_based_on_Bird_thesis, 'params': [(8,4,0),(8,4,1),(8,4,2),(8,5,0),(8,5,1),(8,5,2),(9,4,0),(9,4,1),(9,4,2),(9,5,0),(9,5,1),(9,5,2),(10,4,0),(10,4,1),(10,4,2),(10,5,0),(10,5,1),(10,5,2),(11,4,0),(11,4,1),(11,4,2),(11,5,0),(11,5,1),(10,5,2),(12,5,0),(12,5,1),(12,5,2),(12,6,0),(12,6,1),(12,6,2)],'results':[]}
    #  ]

    configs=[
     {'algo': naive_backtracking_based_on_Bird_thesis, 'params': [(10,4,2),(10,5,2),(11,4,2),(10,5,2),(12,5,2),(12,6,2)],'results':[]},
     {'algo': naive_backtracking_based_on_Bird_thesis, 'params': [(10, 4, 1), (10, 5, 1), (11, 4, 1), (11, 5, 1), (12, 5, 1), (12, 6, 1)], 'results': []}
     ]

    data={'algo':[],'n':[],'gamma':[],'bounding_strategy_type':[],'tree_size':[],'time':[]}
    with Pool(max(1,os.cpu_count()-1)) as p:
        for config in configs:
           config['results']=p.map(config['algo'], config['params'])
           for x in range(len(config['params'])):
              data['algo'].append(config['algo'].__name__)
              data['n'].append(config['params'][x][0])
              data['gamma'].append( config['params'][x][1])
              data['bounding_strategy_type'].append(config['params'][x][2])
              data['tree_size'].append(config['results'][x][1])
              data['time'].append(config['results'][x][2].seconds)
           print(config['algo'])
    pd.DataFrame(data).to_csv("exp_res.csv",index=False)
