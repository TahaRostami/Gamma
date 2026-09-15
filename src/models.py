from ortools.sat.python import cp_model
import collections
from params import halved_universes, slack


def build(k, e, a, b, cuts=True):
    """Return (model, z, status_string).  model is None if the quadruple is
    structurally impossible, in which case status_string says why."""
    Wo, We, kappa = halved_universes(k, e, a, b)
    S = slack(k, e, a, b)
    if S is None or S < 0 or S % 2:
        return None, None, f"slack invalid (S={S})"

    uni = {'o': collections.Counter(Wo), 'e': collections.Counter(We)}
    npairs = {'o': kappa, 'e': k - kappa}
    half = S // 2

    md = cp_model.CpModel()
    z = {}
    cov = collections.defaultdict(list)   # value v -> [vars emitting v]
    minterm = {'o': [], 'e': []}   # (var, X) for the pair minimum
    thresh = {'o': collections.defaultdict(list),   # X -> vars whose minimum is X
              'e': collections.defaultdict(list)}

    for tag, theta in (('o', 1), ('e', 0)):
        vals = sorted(uni[tag])
        inc = {X: [] for X in vals}
        for idx, X in enumerate(vals):
            for Y in vals[idx + 1:]:
                d, s = Y - X, X + Y + theta   # the two emitted values
                if d < 1 or d > k or s > k:
                    continue   # candidate pair retained only
                cap = min(uni[tag][X], uni[tag][Y])
                var = md.NewIntVar(0, cap, f'z{tag}_{X}_{Y}')
                z[(tag, X, Y)] = var
                cov[d].append(var)
                cov[s].append(var)
                inc[X].append(var)
                inc[Y].append(var)
                minterm[tag].append((var, X))
                thresh[tag][X].append(var)
        # every occurrence of every halved value is in exactly one pair
        for X in vals:
            md.Add(sum(inc[X]) == uni[tag][X])

    # every coordinate magnitude is emitted exactly twice
    for v in range(1, k + 1):
        if not cov[v]:
            return None, None, f"value {v} is not emitted by any candidate pair"
        md.Add(sum(cov[v]) == 2)

    # better to disable it in practice; it was mainly experimental to check something during research :)
    if cuts:
        ext = {}
        for tag in ('o', 'e'):
            W = sorted(v for v, c in uni[tag].items() for _ in range(c))
            ext[tag] = sum(W[:npairs[tag]])
            expr = sum(X * var for var, X in minterm[tag])
            md.Add(expr >= ext[tag])                 
            md.Add(expr <= ext[tag] + half)     
            cum, run = 0, []
            for j in sorted(uni[tag]):                   
                cum += uni[tag][j]
                run += thresh[tag][j]
                need = min(cum, npairs[tag]) - half
                if need > 0 and len(run) < len(minterm[tag]):
                    md.Add(sum(run) >= need)
        md.Add(sum(X * var for var, X in minterm['o']) +
               sum(X * var for var, X in minterm['e'])
               == ext['o'] + ext['e'] + half)

    return md, z, 'ok'


def extract(solver, z):
    """Solver assignment that gives list of matched pairs (tag, X, Y) with multiplicity."""
    pairs = []
    for (tag, X, Y), var in z.items():
        n = solver.Value(var)
        pairs += [(tag, X, Y)] * n
    return pairs
