"""
This script checks whether all models in a given set are valid domination sets for the queen domination problem
on an n x n chessboard. Additionally, it verifies if any of the models contain redundant queens, meaning that
removing a queen from the set still results in a valid domination set.

Note: The code is carefully designed with a focus on correctness and clarity rather than optimization for performance.
"""

import json

# Load the models from the JSON file
with open('n_19_gamma_10_stat_results.json', 'r') as json_file:
    models = [set(model) for model in json.load(json_file)['models']]

def get_queen_dom_graph(n):
    """
    Returns the graph representation of the queen domination problem on an n x n chessboard.

    :param n: The size of the chessboard (nxn).
    :return: A dictionary representing the graph, where each vertex corresponds to a square on the board,
             and the edges represent the squares a queen on that vertex can dominate.
    """
    G = {}
    # To ensure compatibility with SAT solvers, indices start from 1 and end at n^2.
    V = [i + 1 for i in range(n * n)]
    for i in range(len(V)):
        N = [V[i]]
        r, c = i // n, i % n
        # Add all squares in the same row.
        N += V[r * n:r * n + n]
        # Add all squares in the same column.
        N += V[c::n]
        # Add all squares in the same diagonal (from top left to bottom right).
        N += [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
        # Add all squares in the same diagonal (from top right to bottom left).
        N += [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
        N = set(N)
        G[V[i]] = N
    return G

# Generate the graph for an n=19 chessboard.
G = get_queen_dom_graph(19)
all_vertices = set(G.keys())

def is_dom_set(P):
    """
    Checks if a given set of vertices forms a domination set.

    :param P: A set of vertices (squares) on the chessboard.
    :return: True if the set P dominates all vertices in the graph, otherwise False.
    """
    return set().union(*[G[partial_sol] for partial_sol in P]) == all_vertices

def has_redundancy(model):
    """
    Checks if a given model has any redundancy, i.e., if any queen can be removed while still dominating the board.

    :param model: A set of vertices representing the positions of queens on the chessboard.
    :return: True if the model has redundancy, otherwise False.
    """
    res = False
    for p in model:
        if is_dom_set(model.difference({p})):
            res = True
            break
    return res

def has_any_model_redundancy(models):
    """
    Checks if any of the models in the provided list have redundancy.

    :param models: A list of models, where each model is a set of vertices representing queen positions.
    :return: True if any model has redundancy, otherwise False.
    """
    is_there_a_model_with_redundancy = False
    for model in models:
        # Ensure all claimed models are valid domination sets; otherwise, raise an assertion error.
        assert is_dom_set(model) == True

        # Check if the valid domination set has redundancy.
        if has_redundancy(model):
            is_there_a_model_with_redundancy = True
            break
    return is_there_a_model_with_redundancy

# Output whether any of the claimed models have redundancy.
print('Do any of the claimed models contain redundancy?', 'YES' if has_any_model_redundancy(models) else 'NO')
