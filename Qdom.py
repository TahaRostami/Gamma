import sys
import argparse
import itertools
from pysat.card import CardEnc, EncType, ITotalizer
from pysat.solvers import Solver


# CUBER
def boxes(n, g):
    """All boxes (a, b, c, d) we have to try, one from each symmetry class."""
    result = []
    for left, right, below, above in itertools.product(range(n), repeat=4):
        if left + right > min(g, n - 2) or below + above > min(g, n - 2):
            continue
        same_class = [cols + rows
                      for (p, q, r, s) in ((left, right, below, above), (below, above, left, right))
                      for cols in ((p, q), (q, p))
                      for rows in ((r, s), (s, r))]
        if (left, right, below, above) == min(same_class):
            result.append((left + 1, n - right, below + 1, n - above))
    return result


# SAT ENCODER
def formula(n, gamma, box):
    """The SAT formula for one box. Returns (clauses, Q) with Q[(x, y)] = queen variable of square (x, y)."""
    a, b, c, d = box
    g = gamma
    delta = 2 * g - n
    N = range(1, n + 1)
    clauses = []
    top = [0]   # largest variable number used so far

    def new():
        top[0] += 1
        return top[0]

    def add(card):
        # add a PySAT cardinality constraint
        clauses.extend(card.clauses)
        top[0] = max(top[0], card.nv)

    # Variables
    Q = {(x, y): new() for x in N for y in N}   # a queen stands on (x, y)
    ROW = {y: new() for y in N}   # row y is active (i.e., contains a queen)
    COL = {x: new() for x in N}   # column x is active
    DIA = {k: new() for k in range(1 - n, n)}   # diagonal x - y = k is active
    ANT = {t: new() for t in range(2, 2 * n + 1)}   # anti-diagonal  x + y = t is active

    def lines(x, y):
        # the four lines through (x, y)
        return [ROW[y], COL[x], DIA[x - y], ANT[x + y]]

    # map each line variable to the queen variables on that line
    queens_on = {}
    for (x, y), q in Q.items():
        for L in lines(x, y):
            if L not in queens_on:
                queens_on[L] = []
            queens_on[L].append(q)

    # Domination Encoding via Line Variables

    # an active line contains a queen
    for L, qs in queens_on.items():
        clauses.append([-L] + qs)

    # a queen activates all four lines through its square
    for (x, y), q in Q.items():
        for L in lines(x, y):
            clauses.append([-q, L])

    # every square lies on an active line
    for (x, y) in Q:
        clauses.append(lines(x, y))

    # card encoding: <= g queens
    by_row = [Q[(x, y)] for y in N for x in N]
    add(CardEnc.atmost(lits=by_row, bound=g, top_id=top[0], encoding=EncType.mtotalizer))
    # no need anymore: since the per-type <= g bounds imply <= 4g active lines as well
    # longest_first = sorted(queens_on, key=lambda L: -len(queens_on[L]))
    # add(CardEnc.atmost(lits=longest_first, bound=4 * g, top_id=top[0], encoding=EncType.mtotalizer))



    # Box Clauses
    for x in N:
        if x in (a, b):
            clauses += [[-Q[(x, y)]] for y in N]   # columns a and b are empty
        elif x < a or x > b:
            clauses.append([Q[(x, y)] for y in N])   # a column outside the box contains a queen
            clauses.append([COL[x]])
    for y in N:
        if y in (c, d):
            clauses += [[-Q[(x, y)]] for x in N]   # rows c and d are empty
        elif y < c or y > d:
            clauses.append([Q[(x, y)] for x in N])   # a row outside the box contains a queen
            clauses.append([ROW[y]])


    # Counting hints
    # excess
    excess = {}
    for name, group in (("row", ROW), ("col", COL), ("dia", DIA), ("ant", ANT)):
        lits = list(group.values())
        m = len(lits)
        add(CardEnc.atmost(lits=lits, bound=g, top_id=top[0], encoding=EncType.mtotalizer))   # <= g active lines
        # excess >= j  <=>  at least m - g + j lines of the group are inactive.
        # ITotalizer over the negated line variables: counter.rhs[k - 1] is forced true when >= k are inactive.
        counter = ITotalizer(lits=[-L for L in lits], ubound=m, top_id=top[0])
        clauses.extend(counter.cnf.clauses)
        top[0] = max(top[0], counter.top_id)
        excess[name] = [counter.rhs[m - g + j - 1] for j in range(1, 2 * delta + 3) if 1 <= m - g + j <= m]

    def side_constraint(side, straight):
        """side = squares of V (or H), straight = 'row' for V, 'col' for H."""
        waste = []
        # over-coverage. for each side square, create one waste literal for each additional active line beyond the first.
        for (x, y) in side:
            through = [DIA[x - y], ANT[x + y]]   # active lines that can cover this square

            # add the row/column unless it is one of the empty boundary lines
            if y not in (c, d):
                through.append(ROW[y])
            if x not in (a, b):
                through.append(COL[x])

            # if at least t lines are active, the t-th coverage literal is forced true.
            # thus, 2 active lines contribute 1 waste, and 3 contribute 2.
            for t in range(2, len(through) + 1):   # o is forced true when t of them are active
                o = new()
                for some in itertools.combinations(through, t):
                    clauses.append([-L for L in some] + [o])
                waste.append(o)

        # classify each (anti-)diagonal by how many squares of the side it contains.
        twice = []
        for group, index_of in ((DIA, lambda x, y: x - y), (ANT, lambda x, y: x + y)):
            for index, L in group.items():
                hits = sum(1 for (x, y) in side if index_of(x, y) == index)
                if hits == 0:
                    waste.append(L)   # line covers nothing here
                elif hits == 2:
                    twice.append(L)   # line meets the side twice

        # IMPORTANT NOTE
        # row (or column) excess has weight two in the lemma, so its literals are listed twice.
        # fortunately, PySAT counts a repeated literal twice.
        # alternative without repeated literals: for each literal e in excess[straight] create a fresh
        # variable e2 = new(), add the clauses [-e, e2] and [e, -e2] (so e2 <-> e), and list e and e2 once each.
        waste += excess[straight] + excess[straight]
        waste += excess["dia"] + excess["ant"]

        # final constraints.
        # waste <= twice + 2*delta. with twice = len(twice) - (number of inactive lines in `twice`):
        literals = waste + [-L for L in twice]
        budget = len(twice) + (2 * delta)
        if budget == 0:   # special case with zero waste allowed
            clauses.extend([[-lit] for lit in literals])   # every literal must be false, so no cardinality encoding is needed
        elif budget < len(literals):
            add(CardEnc.atmost(lits=literals, bound=budget, top_id=top[0], encoding=EncType.totalizer))

    V = [(x, y) for x in (a, b) for y in range(c, d + 1)]
    H = [(x, y) for y in (c, d) for x in range(a, b + 1)]
    side_constraint(V, "row")
    side_constraint(H, "col")
    return clauses, Q


# Helpers
def dominates(n, queens):
    """Independent check that a set of queens attacks or occupies every square."""
    rows = {y for x, y in queens}
    cols = {x for x, y in queens}
    dias = {x - y for x, y in queens}
    ants = {x + y for x, y in queens}
    return all(y in rows or x in cols or x - y in dias or x + y in ants
               for x in range(1, n + 1) for y in range(1, n + 1))

def canonical(n, queens):
    """Smallest of the images of a set of queens under the symmetries of the board."""
    m = n + 1
    images = {
        tuple(sorted(image(x, y) for x, y in queens))
        for image in (
            lambda x, y: (x, y), lambda x, y: (m - x, y), lambda x, y: (x, m - y), lambda x, y: (m - x, m - y),
            lambda x, y: (y, x), lambda x, y: (m - y, x), lambda x, y: (y, m - x), lambda x, y: (m - y, m - x),
        )
    }
    return min(images), len(images)


# MAIN
def main():
    parser = argparse.ArgumentParser(description="Queen domination encoding via box splitting and hint constraints.")
    parser.add_argument("n", type=int, help="chessboard of size nxn")
    parser.add_argument("gamma", type=int, nargs="?", help="number of queens (default: ceil(n/2))")
    parser.add_argument("--enumerate", action="store_true", help="enumerate all dominating sets of at most gamma queens, up to isomorphism")
    parser.add_argument("--out", type=str, help="with --enumerate: write one solution per line to this file")
    args = parser.parse_args()

    n = args.n
    gamma = args.gamma if args.gamma is not None else (n + 1) // 2
    if gamma > n - 2:
        parser.error("the box split needs two empty rows and two empty columns, so gamma <= n - 2")

    all_boxes = boxes(n, gamma)
    conflicts = 0
    seconds = 0.0
    classes = {}   # canonical solution (only used with --enumerate)

    for number, box in enumerate(all_boxes, start=1):
        clauses, Q = formula(n, gamma, box)
        with Solver(name="cadical195", bootstrap_with=clauses, use_timer=True) as solver:
            while solver.solve():
                model = set(solver.get_model())
                queens = sorted(square for square, q in Q.items() if q in model)
                assert dominates(n, queens) and len(queens) <= gamma

                if not args.enumerate:
                    print(f"n={n}: {len(queens)} queens dominate the board (box {box}, box {number} of {len(all_boxes)})")
                    print("queens (column, row):", queens)
                    return

                # keep the canonical form of each solution.
                representative, class_size = canonical(n, queens)
                classes[representative] = class_size

                # block this set of queens and look for the next one.
                blocking = [-Q[square] for square in queens]
                if len(queens) < gamma:
                    chosen = set(queens)
                    blocking += [q for square, q in Q.items() if square not in chosen]
                solver.add_clause(blocking)

            conflicts += solver.accum_stats()["conflicts"]
            seconds += solver.time_accum()
        if number % 100 == 0:
            print(f"  {number}/{len(all_boxes)} boxes done" + (f", {len(classes)} solutions so far" if args.enumerate else ""), file=sys.stderr)

    if not args.enumerate:
        print(f"n={n}: no dominating set of {gamma} queens. "
              f"All {len(all_boxes)} boxes unsatisfiable, {conflicts} conflicts, {seconds:.1f}s solver time.")
        return

    print(f"n={n}, gamma={gamma}: {len(classes)} solutions up to isomorphism "
          f"({sum(classes.values())} solutions in total). "
          f"{len(all_boxes)} boxes, {conflicts} conflicts, {seconds:.1f}s solver time.")
    if args.out:
        with open(args.out, "w") as f:
            for representative in sorted(classes):
                f.write(" ".join(f"{x},{y}" for x, y in representative) + "\n")
        print(f"Solutions (column,row) written to: {args.out}")
if __name__ == "__main__":
    main()
