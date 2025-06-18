## Start Without Knowing Any Details?

I solved and verified `qdom_enum_formula/16_9_HILBERT_MEnum.cnf` using `CaDiCaL` and `lrat-trim`, by generating `16` cubes with a custom script. The full process took less than `2` days of computation.

We would like to investigate whether **AlphaMapleSAT** can hopefully reduce the running time further.


## Need Further Details?
Given two positive integers `n` and `gamma`, the goal is to determine whether there exists a domination set of size `gamma` for the queen graph of a corresponding `nxn` chessboard.

You can generate the corresponding CNF formula using `Qdom.py`. Example usage:
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


You can also add symmetry breaking cluases to CNF formula using `AddSymBreak.py`. Example usage:
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
- I used `Unidom`, a fast domination set solver that enumerates all solutions.
- CNF formulas were created to verify the results (i.e., whether Unidom missed any models).
- Then, the number of non-isomorphic solutions was computed.
The solutions and the isomorphism rejection logic are available in another branch (not required for this context).
### CNF Directory Structure
CNFs for verifying Unidom’s results are available in the `qdom_enum_formula` directory for boards up to `n=19`.
- For `n = 12` to `n = 15`, two encoding variants are included for testing purposes.
- The most important instances (used for cubing and further experiments) are those postfixed with `_HILBERT`. These files encode instances using the mtotalizer, with literals sorted according to the Hilbert curve.
### Performance Note
- Runtime increases with `n`, except for `n=16`, which runs much faster than `n=15`.
- The CNF `16_9_HILBERT_MEnum.cnf` was solved and formally verified using `CaDiCaL` and `lrat-trim` with `16` cubes in under `2` days.

  
