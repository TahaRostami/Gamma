from utils import get_top_id
from pysat.card import CardEnc,EncType

def queen_dom_to_SAT(n,gamma,enc_type=EncType.seqcounter):
    """ Encodes the queen domination problem into the SAT problem

    >>> queen_dom_to_SAT(3,1)
    [[1, 2, 3, 4, 5, 7, 9], [1, 2, 3, 4, 5, 6, 8], [1, 2, 3, 5, 6, 7, 9], [1, 2, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8, 9], [2, 3, 4, 5, 6, 8, 9], [1, 3, 4, 5, 7, 8, 9], [2, 4, 5, 6, 7, 8, 9], [1, 3, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9], [-1, 10], [-10, 11], [-2, -10], [-2, 11], [-11, 12], [-3, -11], [-3, 12], [-12, 13], [-4, -12], [-4, 13], [-13, 14], [-5, -13], [-5, 14], [-14, 15], [-6, -14], [-6, 15], [-15, 16], [-7, -15], [-7, 16], [-16, 17], [-8, -16], [-8, 17], [-9, -17]]

    :param n: the number of rows in a nxn chess board
    :param gamma: the size of the domination set
    :param enc_type: the type of cardinality encodings
    :return: corresponding SAT formula
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

    clauses += CardEnc.equals(lits=V, top_id=top_id, bound=gamma, encoding=enc_type).clauses
    #the above(old original enc) and below(new alternative enc) lines are both applicable
    #it is worth mentioning, up to this point, according to my experiments, there is no significant performance difference between these two lines!
    #clauses += CardEnc.atmost(lits=V, top_id=top_id, bound=gamma, encoding=enc_type).clauses
    return clauses
