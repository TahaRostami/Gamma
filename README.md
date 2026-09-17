# Larger Type E Constructions for Queen Domination

## Certificates

Verified certificates are available in the `certificates/` directory.

## Verification

`src/verify_TypeA_and_TypeE.py` checks a certificate from scratch. It is pure Python.

Set the certificate path on the first line of the file:

```python
with open("../certificates/q1585_coords.txt", "r") as f:
```

then run it:

```bash
python3 src/verify_TypeA_and_TypeE.py
```

It either raises an `AssertionError` at the first failed check, or prints the two asymptotic coefficients the configuration supports.

## Search


Requires Python 3.9+ and OR-Tools:

```bash
pip install ortools
```

```bash
python3 src/search.py k [--time TIME] [--seeds SEEDS] [--workers WORKERS] [--no-cuts]
```

`k` may be a single value or a range `KLO:KHI`.

Example:

```bash
python3 src/search.py 148 --time 55 --seeds 5
python3 src/search.py 148 --time 55 --seeds 5 --no-cuts
```


## Notes

- `--workers 1` is the default and is used for the reported timings. With one worker, runs are deterministic for a fixed seed; with multiple workers, it may be non-deterministic.

- Coordinates of the certificates (shared in the repo) are full-board and centred, running over `−(n−1)/2 … (n−1)/2`, and every queen has both coordinates even.
