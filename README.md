# Improved SAT Encoding for the Queen Domination Problem

`Qdom.py` encodes the queen domination problem and can generate both the CNF formula and cubes when requested.

For usage details, run:

```bash
python Qdom.py --help
```

## Solving and Verification Improvements

In addition to improving the encoding, we also improve the solve-and-verify procedure.

Previously, all solutions were enumerated first, then the solver was called once on the resulting UNSAT instance, and finally the proof was verified. We now use `cadical-exhaust`, which performs solving and proof generation during the solving process.

Please install:

- `cadical-exhaust`: https://github.com/curtisbright/cadical-exhaust
- `drat-trim-t`: https://github.com/curtisbright/drat-trim-t

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

It first runs `qdom_run.sh` in `generate` mode to generate the formula and cubes, then iteratively calls it in `solve_and_verify` mode for each cube sequentially.

The script reports:

- total generation time
- per-cube solving time
- total sequential wall-clock time

---

## par_run.sh

`par_run.sh` is the parallel version of `seq_run.sh`.

It first calls `qdom_run.sh` in `generate` mode to generate the formula and cubes. Then it solves and verifies the cubes in parallel using the specified number of cores.

The number of parallel workers is controlled by `--cores`.

Each worker is assigned cubes according to:

```text
cube_id % cores == worker_id
```

For example, with `--cores 4`:

```text
worker 0 solves cubes 0, 4, 8, ...
worker 1 solves cubes 1, 5, 9, ...
worker 2 solves cubes 2, 6, 10, ...
worker 3 solves cubes 3, 7, 11, ...
```

The script reports:

- formula and cube generation time
- parallel solve wall-clock time
- total solving time summed over all workers
- estimated sequential total time
- actual total wall-clock time

---

# Examples

Sequential run:

```bash
./seq_run.sh --n 13 --gamma 7 --cube-vars 5
```

Parallel run using 4 cores:

```bash
./par_run.sh --n 13 --gamma 7 --cube-vars 5 --cores 4
```

The examples above:

- generate a formula for `qdom` with `n=13` and `gamma=7`
- create `2^5` cubes
- solve and verify all cubes
- write solutions for each cube into the `solutions/` directory
