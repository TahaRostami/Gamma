import math

def universe_sizes(k, e):
    """m and K; see the paper"""
    m = (e + 1) // 2
    K = k - m
    return m, K

def Nke(k, e):
    """N(k,e) of condition (F1)."""
    m, K = universe_sizes(k, e)
    return (2 * (k * (k + 1) * (2 * k + 1)
                 - K * (4 * K * K - 1)
                 - 2 * m * (m - 1) * (2 * m - 1))) // 3

def sum_of_two_squares(N):
    """All (a,b) with 0 <= a <= b and a^2 + b^2 = N."""
    out = []
    if N < 0:
        return out
    a = 0
    while 2 * a * a <= N:
        r = N - a * a
        b = math.isqrt(r)
        if b * b == r and b >= a:
            out.append((a, b))
        a += 1
    return out

def halved_universes(k, e, a, b):
    """W_o and W_e of equation (11), as sorted lists, plus kappa."""
    m, K = universe_sizes(k, e)
    Wo, We = [], []
    for v in range(K):
        Wo += [v, v]
    for v in range(1, m):
        We += [v, v]
    if a % 2:
        Wo += [(a - 1) // 2, (b - 1) // 2]
    else:
        We += [a // 2, b // 2]
    Wo.sort()
    We.sort()
    kappa = len(Wo) // 2
    return Wo, We, kappa

def slack(k, e, a, b):
    """S(k,e,a,b) of condition (F3).  Returns None if the halves are ill-formed."""
    m, K = universe_sizes(k, e)
    Wo, We, kappa = halved_universes(k, e, a, b)
    if len(Wo) % 2 or len(We) % 2:
        return None
    if kappa > len(Wo) or k - kappa > len(We):
        return None
    ext_o = 2 * sum(Wo[:kappa]) + kappa     
    ext_e = 2 * sum(We[:k - kappa])           
    T = 2 * (K * K + m * (m - 1)) + a + b
    return T - k * (k + 1) - ext_o - ext_e

def admissible(k, apply_F3=True):
    """Admissible quadruples for this k, as (e,a,b,S), sorted by decreasing S."""
    out = []
    for e in range(1, k - 1, 2):   # e odd, u = k-e-1 >= 1
        N = Nke(k, e)
        if N < 0:
            continue
        for (a, b) in sum_of_two_squares(N):
            if a < 1 or b > 2 * k - 1:   # (F2) range
                continue
            if (a - b) % 2:   # (F2) equal parity
                continue
            if a == e + 1 or b == e + 1:   # (F2) a,b != i
                continue
            _, _, kappa = halved_universes(k, e, a, b)
            if kappa % 2:   # (F2) kappa even
                continue
            S = slack(k, e, a, b)
            if S is None:
                continue
            if apply_F3 and (S < 0 or S % 2):   # (F3)
                continue
            out.append((e, a, b, S))
    out.sort(key=lambda t: -t[3])
    return out

