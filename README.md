# Improved SAT Encoding for the Queen Domination Problem

`Qdom.py` encodes the queen domination problem and can generate both the CNF formula and cubes when requested.

For usage details, run:

```bash
python Qdom.py --help
```

## Solving and Verification Improvements

In addition to improving the encoding, we also improve the solve-and-verify procedure.

Previously, all solutions were enumerated first, then the solver was called once on the resulting UNSAT instance, and finally the proof was verified. We now use `cadical-exhaust`, which performs solving and proof generation incrementally during the solving process.

Please install:

- `cadical-exhaust`: https://github.com/curtisbright/cadical-exhaust
- `drat-trim-t`: https://github.com/curtisbright/drat-trim-t (optional, only needed for proof verification)

After building these tools, place their binaries in the same directory as `Qdom.py`.

---

# Scripts

## qdom_run.sh

`qdom_run.sh` supports three modes:

- `generate`
  - Generates the CNF formula and cubes by calling `Qdom.py`

- `solve`
  - Solves the formula for a given cube ID

- `solve_and_verify`
  - Solves the formula for a given cube ID and verifies the generated proof

---

## seq_run.sh

`seq_run.sh` calls `qdom_run.sh`.

It first runs `qdom_run.sh` in `generate` mode to generate the formula and cubes, then iteratively calls it in `solve_and_verify` mode for each cube.

---

# Example

The following example:

- generates a formula for `qdom` with `n=13` and `gamma=7`
- creates `2^5` cubes
- solves and verifies all cubes sequentially
- writes the solutions for each cube into the `solutions/` directory

```bash
./seq_run.sh --n 13 --gamma 7 --cube-vars 5
```
