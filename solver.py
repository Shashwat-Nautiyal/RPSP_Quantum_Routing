"""Swappable LP/ILP backend with explicit status handling (task-list rule 3).

Statuses: 'optimal', 'infeasible', 'timeout', 'error'.
A timeout is NEVER the same as infeasible.  Callers that need a decision call
`require_decision` which raises SolverTimeout on 'timeout'/'error'.

Backends
  'highs' : scipy.optimize.linprog / milp (HiGHS).  Default, fast, no temp files.
  'pulp'  : PuLP + CBC (cross-checking).  Only used if `pulp` is importable.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

OPTIMAL, INFEASIBLE, TIMEOUT, ERROR = "optimal", "infeasible", "timeout", "error"


class SolverTimeout(RuntimeError):
    """Solver hit its time limit (or failed): the answer is UNKNOWN."""


class Infeasible(RuntimeError):
    """A problem that must be feasible was proven infeasible."""


@dataclass
class LPModel:
    """min c@x  s.t.  A_ub x <= b_ub,  A_eq x = b_eq,  lb <= x <= ub  (+ optional integrality)."""
    c: np.ndarray
    A_ub: sp.csr_matrix | None
    b_ub: np.ndarray | None
    A_eq: sp.csr_matrix | None
    b_eq: np.ndarray | None
    lb: np.ndarray
    ub: np.ndarray
    integrality: np.ndarray | None = None
    meta: dict = field(default_factory=dict)


@dataclass
class SolveResult:
    status: str
    x: np.ndarray | None
    obj: float | None
    seconds: float


def _nz(A):
    return None if A is None or A.shape[0] == 0 else A


def _solve_highs(m: LPModel, time_limit: float) -> SolveResult:
    t0 = time.time()
    integral = m.integrality is not None and np.any(m.integrality)
    try:
        if not integral:
            res = linprog(m.c, A_ub=_nz(m.A_ub), b_ub=None if _nz(m.A_ub) is None else m.b_ub,
                          A_eq=_nz(m.A_eq), b_eq=None if _nz(m.A_eq) is None else m.b_eq,
                          bounds=np.column_stack([m.lb, m.ub]), method="highs",
                          options={"time_limit": float(time_limit)})
        else:
            cons = []
            if _nz(m.A_ub) is not None:
                cons.append(LinearConstraint(m.A_ub, -np.inf, m.b_ub))
            if _nz(m.A_eq) is not None:
                cons.append(LinearConstraint(m.A_eq, m.b_eq, m.b_eq))
            res = milp(m.c, constraints=cons, integrality=m.integrality,
                       bounds=Bounds(m.lb, m.ub), options={"time_limit": float(time_limit)})
    except Exception:  # pragma: no cover - defensive
        return SolveResult(ERROR, None, None, time.time() - t0)
    # scipy status: 0 optimal, 1 iteration/time limit, 2 infeasible, 3 unbounded, 4 other
    status = {0: OPTIMAL, 1: TIMEOUT, 2: INFEASIBLE}.get(res.status, ERROR)
    x = res.x if status == OPTIMAL else None
    return SolveResult(status, x, getattr(res, "fun", None) if status == OPTIMAL else None,
                       time.time() - t0)


def _solve_pulp(m: LPModel, time_limit: float) -> SolveResult:  # pragma: no cover - needs pulp
    import pulp
    t0 = time.time()
    prob = pulp.LpProblem("m", pulp.LpMinimize)
    n = len(m.c)
    integral = m.integrality is not None
    xs = [pulp.LpVariable(f"v{i}", lowBound=None if np.isneginf(m.lb[i]) else float(m.lb[i]),
                          upBound=None if np.isposinf(m.ub[i]) else float(m.ub[i]),
                          cat="Integer" if integral and m.integrality[i] else "Continuous")
          for i in range(n)]
    prob += pulp.lpSum(float(m.c[i]) * xs[i] for i in range(n) if m.c[i] != 0) + 0
    for A, b, eq in ((m.A_ub, m.b_ub, False), (m.A_eq, m.b_eq, True)):
        if A is None or A.shape[0] == 0:
            continue
        A = A.tocsr()
        for r in range(A.shape[0]):
            sl = slice(A.indptr[r], A.indptr[r + 1])
            expr = pulp.lpSum(float(v) * xs[j] for j, v in zip(A.indices[sl], A.data[sl]))
            prob += (expr == float(b[r])) if eq else (expr <= float(b[r]))
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit))
    # CBC reports 'Optimal' for some time-outs; sol_status disambiguates.
    if prob.status == pulp.LpStatusInfeasible:
        st = INFEASIBLE
    elif prob.status == pulp.LpStatusOptimal and prob.sol_status == pulp.LpSolutionOptimalFound:
        st = OPTIMAL
    else:
        st = TIMEOUT
    x = np.array([v.value() or 0.0 for v in xs]) if st == OPTIMAL else None
    return SolveResult(st, x, pulp.value(prob.objective) if st == OPTIMAL else None,
                       time.time() - t0)


def solve_model(m: LPModel, time_limit: float = 60.0, backend: str = "highs") -> SolveResult:
    if backend == "highs":
        return _solve_highs(m, time_limit)
    if backend == "pulp":
        return _solve_pulp(m, time_limit)
    raise ValueError(f"unknown backend {backend!r}")


def require_decision(res: SolveResult, what: str = "") -> SolveResult:
    """Rule 3: timeouts/errors are 'unknown' and abort the caller."""
    if res.status in (TIMEOUT, ERROR):
        raise SolverTimeout(f"solver returned {res.status} ({what}) after {res.seconds:.1f}s")
    return res


class COOBuilder:
    """Small helper to assemble sparse models row by row."""

    def __init__(self):
        self.lb: list[float] = []
        self.ub: list[float] = []
        self._ub_rows: list[tuple[dict, float]] = []
        self._eq_rows: list[tuple[dict, float]] = []

    def var(self, lb=0.0, ub=1.0) -> int:
        self.lb.append(lb)
        self.ub.append(ub)
        return len(self.lb) - 1

    def le(self, coeffs: dict, rhs: float) -> int:
        self._ub_rows.append((coeffs, rhs))
        return len(self._ub_rows) - 1

    def eq(self, coeffs: dict, rhs: float) -> int:
        self._eq_rows.append((coeffs, rhs))
        return len(self._eq_rows) - 1

    @staticmethod
    def _mat(rows, n):
        if not rows:
            return None, None
        r, c, v = [], [], []
        for i, (co, _) in enumerate(rows):
            for j, a in co.items():
                r.append(i), c.append(j), v.append(a)
        A = sp.csr_matrix((v, (r, c)), shape=(len(rows), n))
        return A, np.array([b for _, b in rows], dtype=float)

    def build(self, integrality=None, meta=None) -> LPModel:
        n = len(self.lb)
        A_ub, b_ub = self._mat(self._ub_rows, n)
        A_eq, b_eq = self._mat(self._eq_rows, n)
        return LPModel(np.zeros(n), A_ub, b_ub, A_eq, b_eq, np.array(self.lb, float),
                       np.array(self.ub, float), integrality, meta or {})
