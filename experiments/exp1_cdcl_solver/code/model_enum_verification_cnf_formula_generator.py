"""This code is designed to generate CNF formulas for the model enumeration scenario."""
from pysat.formula import CNF
import argparse

def parse_chessboard(file_content):
    lines = file_content.strip().split('\n')
    parsed_boards = []
    for line in lines:
        if ':' in line or '-' in line or '=' in line:
            continue
        parsed_boards.append([int(item)+1 for item in line.split()[1:]])# for sat solving compatibility
    return parsed_boards

def main():
    parser = argparse.ArgumentParser(description="Hi!")
    parser.add_argument("--baseFormulaFilename", type=str, required=True, help="Queen Dom CNF formula filename")
    parser.add_argument("--modelsFilename", type=str, required=True, help="The filename where satisfying configurations are located. Note, it is assumed this file generated using Unidom and so the indices started from zero.")
    parser.add_argument("--writeFilename", type=str, required=True, help="write the resulting cnf formula")
    args = parser.parse_args()

    #e.g., "formula/n_19_gamma_10_encAtMost_seqcounter_encAtLeast_None.cnf"
    baseFormulaFilename=args.baseFormulaFilename
    #e.g., "all_19_10.txt
    modelsFilename=args.modelsFilename
    #e.g., "model_enum_verification_formula/all_models_enum_verification_n_19_gamma_10_encAtMost_seqcounter_encAtLeast_None.cnf"
    writeFilename=args.writeFilename

    clauses=CNF(from_file=baseFormulaFilename).clauses

    with open(modelsFilename, 'r') as f:
        solutions = parse_chessboard(f.read())

    for sol in solutions:
        clauses.append([-lit for lit in sol])

    cnf_formula = CNF(from_clauses=clauses)
    cnf_formula.to_file(writeFilename)




if __name__ == "__main__":
    main()