import random
from collections import deque

def Algorithm32(G,desired_size=None,ordering_type=None):
    """ A backtracking algorithm for finding a minimum dominating set

    Implementation of the backtracking algorithm for finding a minimum dominating set based on
    what is described in 3.2 Bounding With Fixed Vertex Ordering of William Herbert Bird's thesis titled
    'Computational Methods for Domination Problems'.

    >>> print(Algorithm32([[0, 1, 2, 3, 4, 6, 8], [0, 1, 2, 3, 4, 5, 7], [0, 1, 2, 4, 5, 6, 8], [0, 1, 3, 4, 5, 6, 7], [0, 1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 7, 8], [0, 2, 3, 4, 6, 7, 8], [1, 3, 4, 5, 6, 7, 8], [0, 2, 4, 5, 6, 7, 8]], ordering_type=None))
    [5]

    :param G: adjacency list representation of graph
    :param desired_size: if G has a dominating set of size at most desired_size
    :param ordering_type: None, 'bfs', 'max', 'min', 'random'
    :return: a minimum dominating set; indices are started from 1
    """

    def _find_dominating_set(P,NP,size_of_NP,desired_size,i):
        nonlocal self_G
        nonlocal self_C
        nonlocal self_B
        # |V (G)|
        n=len(self_G)
        if size_of_NP==n:
            if len(P)<len(self_B):
                self_B=P.copy()
        while i<len(NP) and NP[i]:
            i+=1
        k= len(P) + (n-size_of_NP)//(self_delta+1)
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

    def _renumber_graph(G, ordering_type=None):
        def _BFS(G):
            num_vertices = len(G)
            visited = [False] * num_vertices
            result = []
            queue = deque()
            start_vertex = 0
            queue.append(start_vertex)
            visited[start_vertex] = True
            while queue:
                vertex = queue.popleft()
                result.append(vertex)
                for neighbor in G[vertex]:
                    if not visited[neighbor]:
                        queue.append(neighbor)
                        visited[neighbor] = True
            return result

        ordered = [i for i in range(len(G))]
        if ordering_type == 'random':
            random.shuffle(ordered)
        elif ordering_type == 'bfs':
            ordered = _BFS(G)
        elif ordering_type == 'max' or ordering_type == 'min':
            degrees = [len(v) for v in G]
            ordered = sorted(range(len(degrees)), key=degrees.__getitem__)
            if ordering_type == 'max':
                ordered.reverse()

        num_vertices = len(G)
        # Create a mapping from old vertex IDs to new vertex IDs
        vertex_mapping = {old_id: new_id for new_id, old_id in enumerate(ordered)}

        # Create the renumbered graph
        renumbered_graph = [[] for _ in range(num_vertices)]
        for old_id in range(num_vertices):
            for neighbor in G[old_id]:
                renumbered_graph[vertex_mapping[old_id]].append(vertex_mapping[neighbor])

        # Create a reverse mapping function
        reverse_mapping = {new_id: old_id for old_id, new_id in vertex_mapping.items()}

        return renumbered_graph, reverse_mapping
    # G: adj list representation of the graph
    self_G,reverse_mapping= _renumber_graph(G, ordering_type=ordering_type)
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
    _find_dominating_set(P, NP, size_of_NP, desired_size, 0)
    # For numbering consistency
    self_B=[reverse_mapping[item]+1 for item in self_B]
    return self_B



