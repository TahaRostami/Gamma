"""
This code is designed to solve a CNF formula using a SAT solver and store the results.
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
    parser.add_argument("--cubesFilename", type=str,default=None, help="The path of the cubes")
    parser.add_argument("--solver", type=str, required=True, help="e.g., cd15")
    parser.add_argument("--njobs", type=int, default=1, help="number of cores to be used")
    parser.add_argument("--jobid", type=int, default=0, help="job id: [0 ... number of cores to be used]")
    parser.add_argument("--incremental", action="store_true", help="Incremental SAT solving")
    parser.add_argument("--enum", action="store_true", help="Incremental SAT solving")
    parser.add_argument("--proof", action="store_true", help="Generate proof")
    parser.add_argument("--outputDir", type=str,  help="Directory specifying the location of writing the proof")

    args = parser.parse_args()
    fname, extension = os.path.splitext(os.path.basename(args.formulaFilename))
    clauses = CNF(from_file=args.formulaFilename).clauses


    cubes=[]
    if args.cubesFilename is not None:
       with open(args.cubesFilename,'r') as f:
           for item in f.readlines():
               if item.startswith("a "):
                   cubes.append([int(x) for x in item.replace('\n','').split()[1:-1]])

    if len(cubes)==0:
        start_idx, end_idx=0,0
        cubes=[[]]
    else:
        start_idx,end_idx = partition_list(cubes, args.njobs, args.jobid)
        cubes = cubes[start_idx:end_idx]




    if args.incremental:
        with Solver(bootstrap_with=clauses, name=args.solver, use_timer=True, with_proof=args.proof) as solver:
            idx=start_idx
            for cube in cubes:
                sat = solver.solve(assumptions=cube)
                ofname = f"{args.outputDir}{fname}.drup" if end_idx==0 else f"{args.outputDir}{fname}_cube_{idx}.drup"
                with open(ofname, 'w') as f:
                    f.write('c time(sec):' + str(solver.time()) + '\n')
                    if sat:
                        f.write("s SATISFIABLE" + '\n')
                    else:
                        f.write("s UNSATISFIABLE" + '\n')

                    if sat:
                        f.write('v ' + ' '.join([str(item) for item in solver.get_model()]) + '\n')
                    else:
                        if args.proof:
                            for line in solver.get_proof():
                                f.write(line + '\n')
                idx+=1
    else:
        idx = start_idx
        for cube in cubes:
            #print(len(cube),cube) # for debugging purposes
            with Solver(bootstrap_with=clauses, name=args.solver, use_timer=True, with_proof=args.proof) as solver:
                if args.enum:
                    ofname = f"{args.outputDir}{fname}_enum.drup" if end_idx == 0 else f"{args.outputDir}{fname}_enum_cube_{idx}.drup"
                    with open(ofname, 'w') as f:
                        models=list(solver.enum_models(assumptions=cube))
                        f.write('c time(sec):' + str(solver.time_accum()) + '\n')
                        if len(models)>0:
                            f.write("s SATISFIABLE" + '\n')
                            f.write("c COUNT " + str(len(models)) + '\n')
                        else:
                            f.write("s UNSATISFIABLE" + '\n')
                        for m in models:
                            f.write('v ' + ' '.join([str(item) for item in m]) + '\n')
                else:
                    sat = solver.solve(assumptions=cube)
                    ofname = f"{args.outputDir}{fname}.drup" if end_idx == 0 else f"{args.outputDir}{fname}_cube_{idx}.drup"
                    with open(ofname, 'w') as f:
                        f.write('c time(sec):' + str(solver.time()) + '\n')
                        if sat:
                            f.write("s SATISFIABLE" + '\n')
                        else:
                            f.write("s UNSATISFIABLE" + '\n')

                        if sat:
                            f.write('v ' + ' '.join([str(item) for item in solver.get_model()]) + '\n')
                        else:
                            if args.proof:
                                for line in solver.get_proof():
                                    f.write(line + '\n')


            idx += 1

if __name__=="__main__":
   main()
