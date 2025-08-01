import argparse
import numpy as np
from pysat.formula import CNF,IDPool


def generate_board(n):
    """Return a chessboard of size nxn; Top-left is 1, row-major order"""
    return np.arange(1, n * n + 1).reshape((n, n))

def apply_symmetry(board, sym):
    """Apply symmetries using numpy and preserve 1-based top-left logic"""
    """**The parameter k specifies how many times the array is rotated by 90 degrees counterclockwise.**"""
    if sym == 'identity':
        return board
    elif sym == 'rotate90':
        return np.rot90(board, k=1)
    elif sym == 'rotate180':
        return np.rot90(board, k=2)
    elif sym == 'rotate270':
        return np.rot90(board, k=3)
    elif sym == 'flip_horizontal':  # mirror left-right
        return np.fliplr(board)
    elif sym == 'flip_vertical':    # mirror top-bottom
        return np.flipud(board)
    elif sym == 'flip_main_diag':   # transpose across main diagonal
        return np.transpose(board)
    elif sym == 'flip_anti_diag':   # transpose across anti-diagonal
        return np.flipud(np.fliplr(np.transpose(board)))
    else:
        raise ValueError(f"Unknown symmetry: {sym}")

def get_ordering(n, sym='identity'):
    """Get flat list of square numbers after symmetry"""
    board = generate_board(n)
    transformed = apply_symmetry(board, sym)
    return transformed.flatten().tolist()

def add_static_sym_break_clauses(n,filename):
    """Reference: https://www.curtisbright.com/bln/2024/12/24/harveys-sat-encoding-for-lexicographic-ordering/"""
    N=n*n
    cnf = CNF(from_file=filename)
    idpool = IDPool(start_from=cnf.nv + 1)
    X = get_ordering(n, 'identity')

    for sym in [
        'rotate90', 'rotate180', 'rotate270',
        'flip_horizontal', 'flip_vertical',
        'flip_main_diag', 'flip_anti_diag'
    ]:
        for i in range(N + 1):
            idpool.id(f"a_{sym}_{i}")
        Y = get_ordering(n, sym)
        cnf.append([idpool.id(f"a_{sym}_0")])
        cnf.append([idpool.id(f"a_{sym}_{N}")])
        for i in range(1, N + 1):
            cnf.append([idpool.id(f"a_{sym}_{i}"), Y[i - 1], -idpool.id(f"a_{sym}_{i - 1}")])
            cnf.append([idpool.id(f"a_{sym}_{i}"), -X[i - 1], -idpool.id(f"a_{sym}_{i - 1}")])
            cnf.append([Y[i - 1], -X[i - 1], -idpool.id(f"a_{sym}_{i - 1}")])

            # cnf.append([-idpool.id(f"a_{sym}_{i}"),-Y[i-1],idpool.id(f"a_{sym}_{i-1}")])
            # cnf.append([-idpool.id(f"a_{sym}_{i}"), X[i - 1], idpool.id(f"a_{sym}_{i - 1}")])
            # cnf.append([-Y[i - 1], X[i - 1], idpool.id(f"a_{sym}_{i - 1}")])
    return cnf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add symmetry-breaking clauses to a CNF formula encoding the Queen Domination (QDOM) problem.")

    parser.add_argument("--n", type=int,required=True, help="Board size (n x n)")

    parser.add_argument("--input_filename", type=str,required=True,
                        help="Path to the input CNF file")
    parser.add_argument("--output_filename", type=str,required=True,
                        help="Path to the output CNF file where the updated formula with symmetry breaking will be saved.")

    args = parser.parse_args()

    cnf=add_static_sym_break_clauses(args.n,args.input_filename)
    cnf.to_file(args.output_filename)


