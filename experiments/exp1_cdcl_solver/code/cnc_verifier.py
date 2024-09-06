"""
This code is somewhat optional. It verifies whether the output of Cube-and-Conquer is correct or contains bugs.
Running this code typically takes very little time.
"""
from pysat.formula import CNF
import argparse
from pysat.solvers import Solver
import os

def partition_list(items, k, i):
    if k <= 0:
        raise ValueError("Number of partitions (k) must be greater than 0")
    if i < 0 or i >= k:
        raise ValueError("Index (i) must be within the range [0, k-1]")

    n = len(items)
    avg_size = n // k
    remainder = n % k

    start = i * avg_size + min(i, remainder)
    end = start + avg_size + (1 if i < remainder else 0)

    return start,end

def main():
    parser = argparse.ArgumentParser(description="Hi!")
    parser.add_argument("--formulaFilename", type=str, required=True, help="The path of the cnf formula")
    parser.add_argument("--solver", type=str, required=True, help="e.g., cd15")
    parser.add_argument("--cubesFilename", type=str, default=None, help="The path of the cubes")
    parser.add_argument("--outputDir", type=str, help="Directory specifying the location of writing")

    args = parser.parse_args()
    fname, extension = os.path.splitext(os.path.basename(args.formulaFilename))
    clauses = CNF(from_file=args.formulaFilename).clauses

    cubes = []
    if args.cubesFilename is not None:
        with open(args.cubesFilename, 'r') as f:
            for item in f.readlines():
                if item.startswith("a "):
                    cubes.append([int(x) for x in item.replace('\n', '').split()[1:-1]])

    if len(cubes) > 0:
        clauses = clauses + [[int(-1 * c) for c in cube] for cube in cubes]
        with Solver(bootstrap_with=clauses, name=args.solver, use_timer=True, with_proof=True) as solver:
            sat = solver.solve()
            ofname = f"{args.outputDir}{fname}_CnCVerification.drup"
            with open(ofname, 'w') as f:
                f.write('c time(sec):' + str(solver.time()) + '\n')
                if sat:
                    f.write("s SATISFIABLE" + '\n')
                else:
                    f.write("s UNSATISFIABLE" + '\n')
                if sat:
                    f.write('v ' + ' '.join([str(item) for item in solver.get_model()]) + '\n')
                else:
                    for line in solver.get_proof():
                        f.write(line + '\n')


if __name__=="__main__":
   main()






