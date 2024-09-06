"""
This code is designed to encode the queen domination problem of size  k into a SAT problem, resulting in a corresponding CNF formula.
"""
from pysat.card import CardEnc,EncType
from pysat.formula import CNF
import argparse

def get_top_id(clauses):
    """ Given a list of clauses, it returns the maximum id
    :param clauses: a list of lists
    :return:maximum id
    """
    return max([max([abs(item) for item in c]) for c in clauses])

def queen_dom_to_SAT(n,gamma,enc_type_atmost=EncType.seqcounter,enc_type_atleast=EncType.seqcounter):
    """ Encodes the queen domination problem into the SAT problem
    :param n: the number of rows in a nxn chess board
    :param gamma: the size of the domination set
    :param enc_type: the type of cardinality encodings
    :return: corresponding SAT formula
    """

    if enc_type_atmost is None:
        raise Exception("enc_type_atmost must not be None")

    clauses = []
    # To ensure compatibility with SAT solvers, indices start from 1 and end at n^2
    V = [i+1 for i in range(n * n)]
    top_id = V[-1]
    for i in range(len(V)):
        N = [V[i]]
        r, c = i // n, i % n
        # Squares in the same row
        N += V[r * n:r * n + n]
        # Squares in the same column
        N += V[c::n]
        # Squares in the same diagonal (from top left to bottom right)
        N += [V[j] for j in range(len(V)) if r - c == ((j // n) - (j % n))]
        # Squares in the same diagonal (from top right to bottom left)
        N += [V[j] for j in range(len(V)) if r + c == ((j // n) + (j % n))]
        N = list(set(N))
        clauses.append(N)


    clauses += CardEnc.atmost(lits=V, top_id=top_id, bound=gamma, encoding=enc_type_atmost).clauses

    if enc_type_atleast is not None:
        top_id=get_top_id(clauses)
        clauses += CardEnc.atleast(lits=V, top_id=top_id, bound=gamma, encoding=enc_type_atleast).clauses


    return clauses


def main():
    parser = argparse.ArgumentParser(description="Hi!")
    parser.add_argument("--n", type=int, required=True, help="An integer")
    parser.add_argument("--gamma", type=int, required=True, help="An integer")
    parser.add_argument("--atMost", type=str, required=True, help="A string")
    parser.add_argument("--atLeast", type=str, help="A string, default is None")
    parser.add_argument("--path", type=str, required=True, help="A string specifying the location of writing")

    args = parser.parse_args()

    card_atmost=getattr(EncType, args.atMost)
    card_atleast=getattr(EncType,str(args.atLeast),args.atLeast)

    clauses = queen_dom_to_SAT(n=args.n, gamma=args.gamma, enc_type_atmost=card_atmost, enc_type_atleast=card_atleast)
    cnf_formula = CNF(from_clauses=clauses)
    cnf_formula.to_file(f"{args.path}n_{args.n}_gamma_{args.gamma}_encAtMost_{args.atMost}_encAtLeast_{args.atLeast}.cnf")




if __name__ == "__main__":
    main()