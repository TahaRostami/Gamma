## 	γ: Queen Domination via SAT Solving

Efficient Encoding of the Queen Domination Problem into (Boolean satisfiability problem) SAT Using Hilbert Curve Ordering and Static Symmetry Breaking

## Quick Start
Given two positive integers `n` and `gamma`, the goal is to determine whether there exists a domination set of size `gamma` for the queen graph of a corresponding `nxn` chessboard.
You can generate the corresponding (Conjunctive normal form) CNF formula using `Qdom.py`. Example usage:
```
python3 Qdom.py --help

usage: Qdom.py [-h] [--n N] [--gamma GAMMA] [--enc {seqcounter,sortnetwrk,cardnetwrk,mtotalizer,kmtotalizer}]
               [--ordering {NONE,HILBERTCURVE,DOMINATION_DEGREE}] [--visualize] [--plot_solution]
               [--write_dir WRITE_DIR] [--solve]
QDOM problem encoding and optional solving with CaDiCaL.

options:
  -h, --help            show this help message and exit
  --n N                 Board size (n x n)
  --gamma GAMMA         Number of queens per group
  --enc {seqcounter,sortnetwrk,cardnetwrk,mtotalizer,kmtotalizer}
                        Cardinality encoding type
  --ordering {NONE,HILBERTCURVE,DOMINATION_DEGREE}
                        Literal ordering strategy
  --visualize           Plot variable ordering
  --plot_solution       Plot the solution if SAT
  --write_dir WRITE_DIR
                        Directory path to write the CNF file (writing enabled only if specified)
  --solve               Solve the encoded CNF using CaDiCaL and report timing
```


This script adds symmetry-breaking clauses to a CNF formula using AddSymBreak.py. It assumes that variables 1 through n×n represent the squares of an n×n chessboard, following 1-based indexing and row-major order.
```
python3 AddSymBreak.py --help

usage: AddSymBreak.py [-h] --n N --input_filename INPUT_FILENAME --output_filename OUTPUT_FILENAME

Add symmetry-breaking clauses to a CNF formula encoding the Queen Domination (QDOM) problem.

options:
  -h, --help            show this help message and exit
  --n N                 Board size (n x n)
  --input_filename INPUT_FILENAME
                        Path to the input CNF file
  --output_filename OUTPUT_FILENAME
                        Path to the output CNF file where the updated formula with symmetry breaking
                        will be saved.
```
### Note

SAT instances are trivial when `γ` is optimal value of `gamma`. To test method's performance, you can encode with `gamma = γ - 1`, where `γ` is the optimal dominating set size for a given `n x n` board. These become significantly harder and require exhaustive search.

### Some Known Optimal Values

| `n`      | 12      | 13      |     14  |     15  |     16  |
| -------- | ------- |-------- |-------- |-------- |-------- |
| **`γ`**  | **6**   | **7**   | **8**   | **9**   | **9**   |

## Counting Solutions Up to Isomorphism
In another setting, the goal is to count all non-isomorphic solutions:
- Use `Unidom` or another model enumerator to enumerate all solutions.
- Create CNF formulas to verify the results, ensuring that `Unidom` (or other tools) did not miss any models.
- If needed, compute the number of non-isomorphic solutions from the enumerated models.
- Some formulas related to this scenario are stored in `the qdom_enum_formula/` directory.
- all_models.zip contains all solutions (including isomorphic ones) found by our approaches for n≤19.
### `qdom_enum_formula/` Directory Structure
CNFs for verifying Unidom’s results are available in the `qdom_enum_formula` directory for boards up to `n=19`.
- For `n = 12` to `n = 15`, two encoding variants are included for testing purposes.
- The most important instances—used for cubing and further experiments—have filenames containing `_HILBERT`. These encode the problem using the mtotalizer, with literals sorted according to the Hilbert curve.
- Instances with `SymBreak` in their names include symmetry-breaking clauses.

  
