import sys
import collections

sys.setrecursionlimit(100000)

def edges_from_pairs(pairs):
    """Matched pairs -> the emitted value pairs (p,q) with p > q >= 1."""
    E = []
    for t, X, Y in pairs:
        theta = 1 if t == 'o' else 0
        q, p = Y - X, X + Y + theta
        assert p > q >= 1, (t, X, Y, p, q)
        E.append((p, q))
    return E

def orient_cycles(E, k):
    """orient the 2-regular multigraph on {1,...,k}."""
    adj = collections.defaultdict(list)
    for idx, (p, q) in enumerate(E):
        adj[p].append(idx)
        adj[q].append(idx)
    for v in range(1, k + 1):
        assert len(adj[v]) == 2, (v, len(adj[v]))
    used = [False] * len(E)
    out = []
    for start in range(1, k + 1):
        for idx in adj[start]:
            if used[idx]:
                continue
            cur, ei = start, idx
            while True:
                used[ei] = True
                x, y = E[ei]
                nxt = y if x == cur else x
                out.append((cur, nxt))
                cur = nxt
                rem = [j for j in adj[cur] if not used[j]]
                if not rem:
                    break
                ei = rem[0]
            break
    assert len(out) == len(E)
    tails = collections.Counter(u for u, _ in out)
    heads = collections.Counter(v for _, v in out)
    assert all(tails[v] == 1 and heads[v] == 1 for v in range(1, k + 1)), \
        "cycle orientation failed"
    return out

def assign_roles(ordered, a, b):
    """choose, for each edge, which of its two labels takes the d-role."""
    lab = [(u + v, abs(u - v)) for u, v in ordered]
    n = len(lab)
    adj = collections.defaultdict(list)   # label -> [(other label, edge id)]
    for i, (l1, l2) in enumerate(lab):
        adj[l1].append((l2, i))
        adj[l2].append((l1, i))
    AUX = -1
    if a != b:
        adj[b].append((a, AUX))
        adj[a].append((b, AUX))
    for v in adj:
        if len(adj[v]) % 2:
            return None   # no Eulerian orientation
    used = [False] * n
    used_aux = False
    direction = {}   # edge id -> tail label (the d-label)
    ptr = collections.defaultdict(int)
    for start in list(adj):
        if ptr[start] >= len(adj[start]):
            continue
        stack, path = [start], []
        while stack:
            v = stack[-1]
            while ptr[v] < len(adj[v]):
                w, ei = adj[v][ptr[v]]
                if ei == AUX:
                    if used_aux:
                        ptr[v] += 1
                        continue
                    used_aux = True
                elif used[ei]:
                    ptr[v] += 1
                    continue
                else:
                    used[ei] = True
                ptr[v] += 1
                stack.append(w)
                path.append((v, w, ei))
                break
            else:
                stack.pop()
        for (v, _w, ei) in path:
            if ei != AUX:
                direction[ei] = v
    if len(direction) != n:
        return None
    return [direction[i] for i in range(n)]

def build(k, e, a, b, pairs):
    """Matched pairs -> the 2k+1 full-board queen coordinates, or None."""
    m = (e + 1) // 2
    K = k - m
    R = collections.Counter()
    for v in range(1, 2 * K, 2):
        R[v] += 1
    for v in range(2, 2 * m - 1, 2):
        R[v] += 1
    multD = collections.Counter(R); multD[a] += 1
    multS = collections.Counter(R); multS[b] += 1

    E = edges_from_pairs(pairs)
    labs = collections.Counter()
    for p, q in E:
        labs[p + q] += 1
        labs[p - q] += 1
    assert labs == multD + multS, "label multiset mismatch"

    ordered = orient_cycles(E, k)
    D = assign_roles(ordered, a, b)
    if D is None:
        return None
    gotD = collections.Counter(D)
    gotS = collections.Counter()
    for i, (u, v) in enumerate(ordered):
        l1, l2 = u + v, abs(u - v)
        gotS[l2 if D[i] == l1 else l1] += 1
    assert gotD + gotS == labs
    if not (gotD == multD and gotS == multS):
        assert gotD == multS and gotS == multD, "role split is invalid"   # the mirror split

    coords = [(0, 0)]
    for i, (u, v) in enumerate(ordered):
        d = D[i]
        s = (u + v) if d == abs(u - v) else abs(u - v)
        placed = False
        for eps in (1, -1):
            for eta in (1, -1):
                x, y = eps * u, eta * v
                if abs(y - x) == d and abs(x + y) == s:
                    placed = True
                    break
            if placed:
                break
        assert placed, (u, v, d, s)
        coords.append((2 * x, 2 * y))
        coords.append((-2 * x, -2 * y))
    assert len(set(coords)) == 2 * k + 1
    return coords

def write(k, e, coords, fn=None):
    """Write a certificate"""
    n = 4 * k + 1
    fn = fn or f'q{n}_coords.txt'
    with open(fn, 'w') as f:
        f.write(f'{n} {2 * k + 1} {e} {e} {k - e - 1}\n')
        for x, y in sorted(coords):
            f.write(f'{x} {y}\n')
    return fn

