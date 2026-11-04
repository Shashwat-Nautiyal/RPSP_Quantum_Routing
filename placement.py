"""Phase 3 - RPSP part A: Problem (1) and APSP (Algorithm 1)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp

from solver import (INFEASIBLE, OPTIMAL, LPModel, SolverTimeout, require_decision,
                    solve_model)
from topology import is_feasible, link_key


@dataclass
class PlacementResult:
    ps_final: frozenset
    added: list
    status: str = OPTIMAL
    iterations: int = 0
    lp_solves: int = 0
    seconds: float = 0.0
    extra: dict = field(default_factory=dict)


class PlacementModel:
    """Problem (1).  Built once; `fix(u)` tightens a bound (no rebuild).

    Column layout: [S_0..S_{N-1}] + [e^p_a for pair p, directed arc a].
    Requests with the same unordered (s,d) are merged: they impose identical
    constraints (a path is undirected), so this is an exact reduction.
    """

    def __init__(self, G, requests, initial_ps):
        N = G.number_of_nodes()
        assert sorted(G.nodes) == list(range(N)), "nodes must be 0..N-1"
        pairs = sorted({(min(s, d), max(s, d)) for s, d in requests if s != d})
        edges = sorted(link_key(u, v) for u, v in G.edges)
        arcs = edges + [(v, u) for u, v in edges]  # both directions
        A, P = len(arcs), len(pairs)
        au = np.array([a[0] for a in arcs], dtype=np.int64)
        av = np.array([a[1] for a in arcs], dtype=np.int64)
        p_idx = np.repeat(np.arange(P), A)
        a_idx = np.tile(np.arange(A), P)
        ecol = N + p_idx * A + a_idx
        nvars = N + P * A
        ones = np.ones(len(ecol))

        # Problem (1), constraint (1a): out - in = +1 at s, -1 at d, 0 elsewhere
        r_out, r_in = p_idx * N + au[a_idx], p_idx * N + av[a_idx]
        A_eq = sp.csr_matrix((np.concatenate([ones, -ones]),
                              (np.concatenate([r_out, r_in]), np.concatenate([ecol, ecol]))),
                             shape=(P * N, nvars))
        b_eq = np.zeros(P * N)
        for p, (s, d) in enumerate(pairs):
            b_eq[p * N + s] = 1.0
            b_eq[p * N + d] = -1.0

        # Problem (1), constraint (1b): e_uv - S_u - S_v <= 0
        rows = np.arange(P * A)
        A_ub = sp.csr_matrix((np.concatenate([ones, -ones, -ones]),
                              (np.concatenate([rows, rows, rows]),
                               np.concatenate([ecol, au[a_idx], av[a_idx]]))),
                             shape=(P * A, nvars))
        c = np.zeros(nvars)
        c[:N] = 1.0  # objective (1): sum S_u
        lb, ub = np.zeros(nvars), np.full(nvars, np.inf)
        ub[:N] = 1.0  # relaxed (1d): 0 <= S_u <= 1
        lb[list(initial_ps)] = 1.0  # (1c)
        self.N, self.pairs = N, pairs
        self.model = LPModel(c, A_ub, np.zeros(P * A), A_eq, b_eq, lb, ub)

    def fix(self, u: int):
        """Add constraint S_u = 1 (Algorithm 1, line 6)."""
        self.model.lb[u] = 1.0

    def solve_relaxed(self, time_limit=120.0, backend="highs"):
        self.model.integrality = None
        r = require_decision(solve_model(self.model, time_limit, backend), "problem (1) relaxed")
        assert r.status == OPTIMAL, "relaxed Problem (1) should always be feasible"
        return r

    def solve_exact(self, time_limit=60.0, backend="highs"):
        integ = np.zeros(len(self.model.c), dtype=int)
        integ[: self.N] = 1  # (1d): S_u binary
        self.model.integrality = integ
        try:
            return solve_model(self.model, time_limit, backend)
        finally:
            self.model.integrality = None


def apsp(G, requests, initial_ps, time_limit=120.0, backend="highs", batch_size=1,
         model: PlacementModel | None = None) -> PlacementResult:
    """Algorithm 1 (Additional Photon Source Placement).

    Raises SolverTimeout if an LP times out (never treated as 'infeasible')."""
    t0 = time.time()
    ps = set(initial_ps)
    if is_feasible(G, ps, requests):
        return PlacementResult(frozenset(ps), [], seconds=time.time() - t0)
    N = G.number_of_nodes()
    # Algorithm 1, lines 1-2: formulate Problem (1), relax (1d), solve
    model = model or PlacementModel(G, requests, initial_ps)
    res = model.solve_relaxed(time_limit, backend)
    solves, omega, added, it = 1, set(), [], 0
    # Algorithm 1, line 4: loop on an INTEGRAL feasibility test of the current PS set
    while not is_feasible(G, ps, requests):
        it += 1
        assert it <= N, "APSP exceeded N iterations"
        S = res.x[:N]
        cand = [u for u in range(N) if u not in ps and u not in omega]
        assert cand, "all nodes are PS but still infeasible (disconnected graph?)"
        # line 5: argmax S*_u ; ties by degree then id
        cand.sort(key=lambda u: (-round(float(S[u]), 6), -G.degree(u), u))
        for u in cand[:batch_size]:
            omega.add(u), ps.add(u), added.append(u)
            model.fix(u)  # line 6: add S_u = 1
        if is_feasible(G, ps, requests):
            break
        res = model.solve_relaxed(time_limit, backend)  # line 6: re-solve relaxed, update S*
        solves += 1
    # line 7: S_u <- 0 for u not in Omega  (initial PSes remain)
    return PlacementResult(frozenset(ps), added, OPTIMAL, it, solves, time.time() - t0)


def solve_ilp_placement(G, requests, initial_ps, time_limit=60.0, backend="highs"):
    """Exact Problem (1) (RPSP-ILP).  Only for small dense instances.  Returns
    PlacementResult with status 'optimal' | 'timeout' | 'infeasible'."""
    t0 = time.time()
    model = PlacementModel(G, requests, initial_ps)
    r = model.solve_exact(time_limit, backend)
    if r.status != OPTIMAL:
        return PlacementResult(frozenset(initial_ps), [], r.status, seconds=time.time() - t0)
    ps = frozenset(int(u) for u in np.flatnonzero(r.x[: model.N] > 0.5))
    return PlacementResult(ps, sorted(ps - set(initial_ps)), OPTIMAL, 0, 1, time.time() - t0)


def redundant_additions(G, requests, initial_ps, added) -> list:
    """Task 3.4(a): added PSes whose removal keeps the instance feasible."""
    final = set(initial_ps) | set(added)
    return [u for u in added if is_feasible(G, final - {u}, requests)]
