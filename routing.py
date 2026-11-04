"""Phase 4.1-4.4: candidate paths, Problem (3), binary search for T*, RPD (Algorithm 2)."""
from __future__ import annotations

import itertools
from collections import defaultdict
from dataclasses import dataclass

import networkx as nx
import numpy as np

from solver import (INFEASIBLE, OPTIMAL, COOBuilder, Infeasible, LPModel, SolverTimeout,
                    require_decision, solve_model)
from topology import HOP_W, light_subgraph, path_links, shortest_path


# ----------------------------------------------------------------- Task 4.1
def candidate_paths(G, ps_final, requests, k: int = 3):
    """D2/D3: Yen's algorithm (networkx.shortest_simple_paths) on the light subgraph,
    first k paths, ordered by (hops, km).  paths[i] = list of node tuples."""
    Gl = light_subgraph(G, ps_final)
    wfun = lambda u, v, d: HOP_W + d["km"]  # noqa: E731  hop-dominant weight (D1)
    cache, out = {}, []
    for s, d in requests:
        if (s, d) not in cache:
            sp_ = shortest_path(Gl, s, d)
            assert sp_ is not None, f"request {(s, d)} has no light path (run APSP first)"
            paths = [tuple(p) for p in itertools.islice(
                nx.shortest_simple_paths(Gl, s, d, weight=wfun), k)]
            if paths[0] != sp_:  # make candidate 0 == the D1 shortest path exactly
                paths = ([sp_] + [p for p in paths if p != sp_])[:k]
            cache[(s, d)] = paths
        out.append(list(cache[(s, d)]))
    return out


# ----------------------------------------------------------------- Task 4.2
def build_problem3(paths, ps_nodes, T=None, time_indexed=False, integer=False) -> LPModel:
    """Problem (3) (relaxed) or Problem (2) (integer=True) for a FIXED horizon T.

    time_indexed=True : literal formulation with x,y,z,w over slots t=1..T (needs T).
    time_indexed=False: exact aggregated reduction (decision D9): only the final state
        (t=T) matters in (2e),(3h) and (2a) is a per-slot unit capacity, so with
        X = sum_t x the LP is equivalent to
            z_ij <= sum_{u in PS ends(l)} X^u_ijl   for every link l of path (i,j)   [(2b),(2c),(3h)]
            sum_j z_ij >= 1                                                       [(2d),(2e)]
            sum X^u <= T                                                          [(2a) summed over t]
        (a feasible aggregated point is spread evenly: x(t) = X/T).  Verified against the
        literal model in tests/test_routing.py.
    Objective is the feasibility objective 0 (Task 4.2).
    """
    ps = set(ps_nodes)
    b = COOBuilder()
    if integer:
        assert time_indexed, "integer Problem (2) only implemented time-indexed"
    meta = {}
    ends_of = lambda l: [n for n in l if n in ps]  # noqa: E731

    if not time_indexed:
        z = {(i, j): b.var(0.0, 1.0) for i, pl in enumerate(paths) for j in range(len(pl))}
        by_node = defaultdict(list)
        for i, pl in enumerate(paths):
            for j, path in enumerate(pl):
                for l in path_links(path):
                    ends = ends_of(l)
                    assert ends, f"dark link {l} on a relay path"
                    co = {z[(i, j)]: 1.0}
                    for u in ends:
                        xc = b.var(0.0, np.inf)
                        co[xc] = -1.0
                        by_node[u].append(xc)
                    b.le(co, 0.0)  # (2b)+(2c)+(3h)
        for i, pl in enumerate(paths):
            b.le({z[(i, j)]: -1.0 for j in range(len(pl))}, -1.0)  # (2d)+(2e)
        cap0 = len(b._ub_rows)
        for u in sorted(by_node):
            b.le({xc: 1.0 for xc in by_node[u]}, float(T if T is not None else 0))  # (2a)
        meta.update(z_col=z, cap_start=cap0, cap_count=len(by_node), aggregated=True)
        return b.build(meta=meta)

    # ---- literal time-indexed model
    assert T is not None and T >= 1
    x, y, zt, w = {}, {}, {}, {}
    for i, pl in enumerate(paths):
        for j, path in enumerate(pl):
            for t in range(1, T + 1):
                zt[(i, j, t)] = b.var(0, 1)
                for l in path_links(path):
                    y[(i, j, l, t)] = b.var(0, 1)
                    for u in ends_of(l):
                        x[(i, j, l, u, t)] = b.var(0, 1)
        for t in range(1, T + 1):
            w[(i, t)] = b.var(1 if t == T else 0, 1)  # (2e) w_i(T)=1
    # (2a): sum x <= S_u (=1 for PS nodes) per node and slot
    per_ut = defaultdict(dict)
    for (i, j, l, u, t), c in x.items():
        per_ut[(u, t)][c] = 1.0
    for co in per_ut.values():
        b.le(co, 1.0)
    for i, pl in enumerate(paths):
        for j, path in enumerate(pl):
            links = path_links(path)
            for t in range(1, T + 1):
                for l in links:  # (2b): y(t) <= sum_{k<=t} sum_u x(k)
                    co = {y[(i, j, l, t)]: 1.0}
                    for k in range(1, t + 1):
                        for u in ends_of(l):
                            co[x[(i, j, l, u, k)]] = -1.0
                    b.le(co, 0.0)
                # (2c): z(t) <= (1/|L|) sum_l y(t)
                co = {zt[(i, j, t)]: 1.0}
                for l in links:
                    co[y[(i, j, l, t)]] = -1.0 / len(links)
                b.le(co, 0.0)
            if not integer:  # (3h): y(T) = z(T) on every hop
                for l in links:
                    b.eq({y[(i, j, l, T)]: 1.0, zt[(i, j, T)]: -1.0}, 0.0)
        for t in range(1, T + 1):  # (2d): w(t) <= sum_j z(t)
            co = {w[(i, t)]: 1.0}
            for j in range(len(pl)):
                co[zt[(i, j, t)]] = -1.0
            b.le(co, 0.0)
    # (2f) y(0)=0 is implicit: y(1) <= x(1) only (no variable for t=0)
    meta.update(z_col={(i, j): zt[(i, j, T)] for i, pl in enumerate(paths) for j in range(len(pl))},
                aggregated=False, T=T)
    integ = np.ones(len(b.lb), dtype=int) if integer else None
    return b.build(integrality=integ, meta=meta)


def set_T(model: LPModel, T: int):
    """Aggregated model only: change the horizon (RHS of the capacity rows (2a))."""
    assert model.meta["aggregated"]
    s, n = model.meta["cap_start"], model.meta["cap_count"]
    model.b_ub[s:s + n] = float(T)


def forbid(model: LPModel, i, j):
    model.ub[model.meta["z_col"][(i, j)]] = 0.0  # RPD line 6: z_ij(t) = 0


def force(model: LPModel, i, j):
    model.lb[model.meta["z_col"][(i, j)]] = 1.0


def extract_z(model: LPModel, x):
    return {key: float(x[c]) for key, c in model.meta["z_col"].items()}


# ----------------------------------------------------------------- Task 4.3
def min_T(model: LPModel, lo: int, hi: int, cap: int, time_limit=60.0, backend="highs",
          stats: dict | None = None):
    """Smallest integer T >= lo for which the relaxed Problem (3) is feasible.

    Binary search with galloping.  A solver timeout raises SolverTimeout (rule 3);
    it is never interpreted as infeasible.  Returns (T, x)."""
    stats = stats if stats is not None else {}

    def feas(T):
        set_T(model, T)
        r = require_decision(solve_model(model, time_limit, backend), f"problem (3), T={T}")
        stats["lp_solves"] = stats.get("lp_solves", 0) + 1
        return r

    lo = max(1, lo)
    r = feas(lo)
    if r.status == OPTIMAL:
        return lo, r.x
    bad = lo  # largest T known infeasible
    hi = max(hi, bad + 1)
    while True:  # gallop up to a feasible T
        r = feas(hi)
        if r.status == OPTIMAL:
            break
        bad = hi
        if hi >= cap:
            raise Infeasible(f"Problem (3) infeasible even at cap T={cap}")
        hi = min(2 * hi, cap)
    best_x = r.x
    while hi - bad > 1:  # invariant: bad infeasible, hi feasible
        mid = (bad + hi) // 2
        r = feas(mid)
        if r.status == OPTIMAL:
            hi, best_x = mid, r.x
        else:
            bad = mid
    return hi, best_x


# ----------------------------------------------------------------- Task 4.4
@dataclass
class RPDResult:
    chosen: list  # per request: index j of the chosen candidate path
    T_lp: int
    iterations: int
    lp_solves: int


def rpd(paths, ps_nodes, upper_hint=None, forbid_per_iter: int = 1, tol: float = 1e-6,
        time_limit=60.0, backend="highs") -> RPDResult:
    """Algorithm 2 (Progressive Rounding based Relay Path Determination), with the fixes
    listed in the task list:
      * argmin ranges over FRACTIONAL, not-yet-forbidden paths only;
      * the chosen path IS added to F (the paper forgets this);
      * if a request would be left without a path, that path is fixed (z=1) instead;
      * post-processing keeps exactly one path (z=1) per request (fewest hops, then index).
    """
    R = len(paths)
    if R == 0:
        return RPDResult([], 0, 0, 0)
    stats = {}
    model = build_problem3(paths, ps_nodes)  # line 1
    cap = R * max(len(p) - 1 for pl in paths for p in pl)  # D8 upper bound
    hi = max(1, min(cap, upper_hint if upper_hint else cap))
    T, x = min_T(model, 1, hi, cap, time_limit, backend, stats)  # line 3
    allowed = [set(range(len(pl))) for pl in paths]
    F, it = set(), 0  # line 2
    while True:  # line 4
        z = extract_z(model, x)
        frac = sorted((v, i, j) for (i, j), v in z.items()
                      if tol < v < 1 - tol and (i, j) not in F)
        if not frac:
            break
        for v, i, j in frac[:forbid_per_iter]:  # line 5
            if len(allowed[i]) == 1:
                force(model, i, j)
            else:
                allowed[i].discard(j)
                forbid(model, i, j)  # line 6
            F.add((i, j))  # (fix: F is updated)
        T, x = min_T(model, T, T, cap, time_limit, backend, stats)  # line 7 (T* never decreases)
        it += 1
    z = extract_z(model, x)
    chosen = []
    for i, pl in enumerate(paths):
        ones = [j for j in range(len(pl)) if z[(i, j)] > 1 - tol]
        if not ones:  # numerical safety
            ones = [max(range(len(pl)), key=lambda j: z[(i, j)])]
        chosen.append(min(ones, key=lambda j: (len(pl[j]), j)))
    return RPDResult(chosen, T, it, stats.get("lp_solves", 0))


# ----------------------------------------------------------------- exact Problem (2) (tiny instances)
def solve_problem2_exact(paths, ps_nodes, T_max: int, time_limit=60.0, backend="highs"):
    """Smallest T for which the INTEGER time-indexed Problem (2) is feasible.
    Raises SolverTimeout on timeout; returns None if infeasible up to T_max."""
    for T in range(1, T_max + 1):
        m = build_problem3(paths, ps_nodes, T, time_indexed=True, integer=True)
        r = require_decision(solve_model(m, time_limit, backend), f"problem (2), T={T}")
        if r.status == OPTIMAL:
            return T
    return None
