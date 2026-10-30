# γ: Computational Queen Domination

Research artifacts for the **queen domination problem**, organized across separate branches.

---

### Queen Domination by SAT Solving

SAT-based enumeration of minimum dom. sets up to symmetry, with independently verifiable completeness proofs, for boards up to \(n=19\).

- **[v1](https://arxiv.org/abs/2508.11945v1)** ([`sat-solving`](../../tree/sat-solving)): Original SAT encoding with Hilbert-curve literal ordering, symmetry breaking, and Cube-and-Conquer.
- **[v2](https://arxiv.org/abs/2508.11945v2)** ([`gamma-plus`](../../tree/gamma-plus), [ADAM 2026](https://doi.org/10.26493/2590-9770.2033.c47)): Improved line-variable encoding and integrated proof-producing enumeration pipeline.

### Hint and Conquer — [`hint-and-conquer`](../../tree/hint-and-conquer)

SAT-based unsatisfiability proofs using counting hints, establishing six new exact queen domination numbers for even boards up to \(n=38\).

### Larger Type E Constructions — [`upper-bound`](../../tree/upper-bound)

Constraint-programming search for Type E dominating sets, producing constructions up to \(n=1585\) and improved asymptotic upper bounds.

---

### License

Released under the [MIT License](LICENSE).
