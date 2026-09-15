from ortools.sat.python import cp_model
import argparse
import json
import time
import models
import params
import reconstruct

def attempt(k, e, a, b, tl, seed, workers, cuts):
    """One CP-SAT run.  Returns (status, seconds, certificate filename or None)."""
    md, z, st = models.build(k, e, a, b, cuts=cuts)
    if md is None:
        return 'N/A:' + st, 0.0, None
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tl
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    if seed:
        s.parameters.randomize_search = True
        s.parameters.search_random_variable_pool_size = 5
    t0 = time.time()
    r = s.Solve(md)
    dt = time.time() - t0
    if r in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        pairs = models.extract(s, z)
        C = reconstruct.build(k, e, a, b, pairs)
        if C is None:
            return 'ROLE_ASSIGN_FAILED', dt, None
        fn = reconstruct.write(k, e, C)
        with open(f'pairs_q{4 * k + 1}.txt', 'w') as f:
            f.write('\n'.join(f'{t} {X} {Y}' for t, X, Y in pairs))
        return 'SOLVED', dt, fn
    return s.StatusName(r), dt, None

def search(k, tl, nseed, workers, cuts):
    """Main search algorithm for a single k.  Returns a list of per-quadruple outcomes."""
    out = []
    for (e, a, b, S) in params.admissible(k):    # already sorted by decreasing S
        record = {'k': k, 'e': e, 'a': a, 'b': b, 'S': S,
                  'status': 'UNKNOWN', 'seconds': 0.0, 'certificate': None}
        for seed in range(nseed):
            status, dt, fn = attempt(k, e, a, b, tl, seed, workers, cuts)
            record['seconds'] += dt
            if status == 'SOLVED':
                record.update(status='SOLVED', certificate=fn, solve_seconds=dt,
                              seed=seed)
                break
            if status == 'INFEASIBLE':   # seed-independent; stop early
                record['status'] = 'INFEASIBLE'
                break
            if status.startswith('N/A'):
                record['status'] = status
                break
            record['status'] = status   # UNKNOWN: try the next seed
        coef = (3 * k + 5) / (6 * k + 3)
        mark = '***' if record['status'] == 'SOLVED' else '   '
        print(f"{mark} k={k:4d} n={4*k+1:5d} e={e:4d} a={a:4d} b={b:4d} S={S:4d} "
              f"{record['status']:12s} {record['seconds']:7.1f}s "
              f"coef={coef:.7f}"
              + (f" -> {record['certificate']}" if record['certificate'] else ''),
              flush=True)
        out.append(record)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('k', help='board parameter k, or a range KLO:KHI')
    ap.add_argument('--time', type=float, default=60.0, help='per-run limit t (s)')
    ap.add_argument('--seeds', type=int, default=5, help='runs per quadruple r')
    ap.add_argument('--workers', type=int, default=1,help='CP-SAT workers (1 keeps the solve deterministic per seed)')
    ap.add_argument('--no-cuts', action='store_true',help='disable the cuts')
    args = ap.parse_args()

    if ':' in args.k:
        lo, hi = (int(x) for x in args.k.split(':'))
        ks = range(hi, lo - 1, -1)
        tag = f'{lo}-{hi}'
    else:
        ks = [int(args.k)]
        tag = args.k

    allout = []
    for k in ks:
        allout += search(k, args.time, args.seeds, args.workers, not args.no_cuts)

    fn = f'outcomes_{tag}.json'
    json.dump(allout, open(fn, 'w'), indent=1)
    n_s = sum(1 for r in allout if r['status'] == 'SOLVED')
    n_i = sum(1 for r in allout if r['status'] == 'INFEASIBLE')
    n_u = len(allout) - n_s - n_i
    print(f"\n{len(allout)} quadruples: {n_s} solved, {n_i} refuted, "
          f"{n_u} undecided at the time limit  ->  {fn}")

if __name__ == '__main__':
    main()
