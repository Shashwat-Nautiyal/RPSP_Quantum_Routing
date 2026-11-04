"""Phase 4.5-4.7 and 5.2: link demand, PSP (Algorithm 3), schedule + checker, greedy (GD)."""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp

from solver import OPTIMAL, LPModel, require_decision, solve_model
from topology import link_key, path_links

EPS = 1e-6


# ----------------------------------------------------------------- Task 4.5
def link_demands(chosen_paths, ps_nodes) -> dict:
    """c_uv: number of chosen relay paths through every link (keys: canonical link)."""
    c = defaultdict(int)
    for path in chosen_paths:
        for l in path_links(path):
            assert l[0] in ps_nodes or l[1] in ps_nodes, f"dark link {l} on a relay path"
            c[l] += 1
    return dict(c)


def ps_ends(l, ps_nodes):
    return [n for n in l if n in ps_nodes]


# ----------------------------------------------------------------- Task 4.6
@dataclass
class PSPResult:
    p: dict  # (u, v) -> number of slots PS u is provisioned to link (u,v)
    T: int  # integer makespan = max_u load
    T_lp: float  # optimum of the relaxed Problem (4)
    load: dict


def _solve_min_T(var_count, A_ub, b_ub, A_eq, b_eq, ub, time_limit, backend, what):
    """min T where T is the LAST variable."""
    c = np.zeros(var_count)
    c[-1] = 1.0
    m = LPModel(c, A_ub, b_ub, A_eq, b_eq, np.zeros(var_count), ub)
    r = require_decision(solve_model(m, time_limit, backend), what)
    assert r.status == OPTIMAL, f"{what} must be feasible"
    return r


def psp(c: dict, ps_nodes, time_limit=60.0, backend="highs") -> PSPResult:
    """Algorithm 3 with the corrections from the task list (Known issues)."""
    p = defaultdict(int)  # directed (u -> v): PS u serves link (u,v)
    m = defaultdict(int)  # per-node load committed so far
    B = []  # two-PS-end links
    # Algorithm 3, lines 1-3: links with exactly one PS end
    for l, cnt in sorted(c.items()):
        ends = ps_ends(l, ps_nodes)
        assert ends, f"dark link {l}"
        if len(ends) == 1:
            u = ends[0]
            v = l[0] if l[1] == u else l[1]
            p[(u, v)] += cnt
            m[u] += cnt
        else:
            B.append(l)
    T_lp = float(max(m.values(), default=0))
    if B:
        nB = len(B)
        nodes = sorted({n for l in B for n in l} | set(m))
        row = {n: i for i, n in enumerate(nodes)}
        # Problem (4): vars p_ab (col 2k), p_ba (col 2k+1), T (last)
        nv = 2 * nB + 1
        eq = sp.lil_matrix((nB, nv))
        b_eq = np.zeros(nB)
        ub = sp.lil_matrix((len(nodes), nv))
        b_ub = np.zeros(len(nodes))
        for k, (a, bb) in enumerate(B):
            eq[k, 2 * k] = eq[k, 2 * k + 1] = 1  # (4a)
            b_eq[k] = c[(a, bb)]
            ub[row[a], 2 * k] = 1  # (4b): sum_v p_uv + m_u <= T
            ub[row[bb], 2 * k + 1] = 1
        for n in nodes:
            ub[row[n], nv - 1] = -1
            b_ub[row[n]] = -m.get(n, 0)
        bounds = np.full(nv, np.inf)
        r = _solve_min_T(nv, ub.tocsr(), b_ub, eq.tocsr(), b_eq, bounds, time_limit, backend,
                         "problem (4)")
        phat, T_lp = r.x, float(r.x[-1])
        # lines 4-6: concretize integer parts; C = links whose p-hat is integral
        frac = []
        for k, (a, bb) in enumerate(B):
            pa = float(phat[2 * k])
            ra = round(pa)
            if abs(pa - ra) < EPS:  # link in C: fully concretized
                ra = int(min(max(ra, 0), c[(a, bb)]))
                p[(a, bb)] += ra
                p[(bb, a)] += c[(a, bb)] - ra
                m[a] += ra
                m[bb] += c[(a, bb)] - ra
            else:
                fa = int(math.floor(pa))
                fb = c[(a, bb)] - fa - 1  # floor(p_ba) since p_ba = c - p_ab
                p[(a, bb)] += fa
                p[(bb, a)] += fb
                m[a] += fa
                m[bb] += fb
                frac.append((a, bb))  # B - C: exactly one key left on this link
        if frac:
            # Problem (5): q_k = p_ab share of the last key (p_ba = 1 - q_k).  m is the
            # UPDATED m (floors counted once -- fixes Algorithm 3 line 7).
            nf = len(frac)
            nodes5 = sorted({n for l in frac for n in l})
            row5 = {n: i for i, n in enumerate(nodes5)}
            ub5 = sp.lil_matrix((len(nodes5), nf + 1))
            b5 = np.zeros(len(nodes5))
            for k, (a, bb) in enumerate(frac):
                ub5[row5[a], k] += 1  # + q_k
                ub5[row5[bb], k] += -1  # (1 - q_k) = 1 - q
                b5[row5[bb]] -= 1
            for n in nodes5:
                ub5[row5[n], nf] = -1
                b5[row5[n]] -= m.get(n, 0)  # sum_v p_uv + m_u <= T   (5b)
            bnd = np.concatenate([np.ones(nf), [np.inf]])
            r5 = _solve_min_T(nf + 1, ub5.tocsr(), b5, None, None, bnd, time_limit, backend,
                              "problem (5)")
            # lines 9-13 restricted to B - C: round p-double-dot >= 0.5
            for k, (a, bb) in enumerate(frac):
                if r5.x[k] >= 0.5 - 1e-9:
                    p[(a, bb)] += 1
                    m[a] += 1
                else:
                    p[(bb, a)] += 1
                    m[bb] += 1
    p = {k: v for k, v in p.items() if v > 0}
    load = defaultdict(int)
    for (u, v), n in p.items():
        load[u] += n
    T = max(load.values(), default=0)
    # --- invariants (Task 4.6 assertions)
    for l, cnt in c.items():
        assert p.get((l[0], l[1]), 0) + p.get((l[1], l[0]), 0) == cnt, f"demand mismatch on {l}"
        for (u, v) in ((l[0], l[1]), (l[1], l[0])):
            assert p.get((u, v), 0) == 0 or u in ps_nodes
    assert T >= math.ceil(T_lp - 1e-6), (T, T_lp)
    assert T <= 2 * T_lp + 1e-6, f"Theorem 2 violated: T={T}, 2*T_lp={2 * T_lp}"
    return PSPResult(p, int(T), T_lp, dict(load))


# ----------------------------------------------------------------- Task 4.7
def schedule_from_p(p: dict):
    """Per-slot schedule: list over slots of {ps_node: link}.  Order per node is irrelevant
    to the makespan (paper); we use sorted link order."""
    seq = defaultdict(list)
    for (u, v), n in sorted(p.items()):
        seq[u] += [link_key(u, v)] * n
    T = max((len(s) for s in seq.values()), default=0)
    return [{u: s[t] for u, s in seq.items() if t < len(s)} for t in range(T)]


def verify_schedule(chosen_paths, ps_nodes, schedule):
    """Simulate the slots; assign each key on a link to the next waiting request
    using that link; return (completion slot per request, makespan).
    Raises AssertionError on any violation."""
    queue = defaultdict(list)
    for r, path in enumerate(chosen_paths):
        for l in path_links(path):
            queue[l].append(r)
    served = defaultdict(int)
    arrive = [dict() for _ in chosen_paths]
    for t, slot in enumerate(schedule, start=1):
        for u, l in slot.items():
            assert u in ps_nodes and u in l, f"PS {u} cannot serve link {l}"
            idx = served[l]
            if idx < len(queue[l]):
                arrive[queue[l][idx]][l] = t
                served[l] += 1
    done = []
    for r, path in enumerate(chosen_paths):
        ls = path_links(path)
        assert all(l in arrive[r] for l in ls), f"request {r} not established in {len(schedule)} slots"
        done.append(max((arrive[r][l] for l in ls), default=0))
    return done, max(done, default=0)


# ----------------------------------------------------------------- Task 5.2 (D4)
def greedy_provisioning(c: dict, ps_nodes, mode: str = "coordinated"):
    """D4.  Each slot every PS serves the adjacent link with the most remaining unmet demand
    (ties: smaller link key).  A two-PS-end link is 'owned' by the end with the smaller
    pending one-end load (ties: smaller id) -- i.e. the one with more remaining capacity;
    a PS left idle after that pass helps on any adjacent link that still has demand.
    mode='naive' (sensitivity variant, NOT the D4 default): PSes decide independently from the
    demand at the start of the slot, so two PSes may both serve the last key of a shared link
    (one key is wasted); there is no ownership rule and no idle-helper pass.
    Returns the schedule (list of {ps: link}); its length is the slot count."""
    rem = {l: n for l, n in c.items()}
    links_of = defaultdict(list)
    for l in sorted(rem):
        for u in ps_ends(l, ps_nodes):
            links_of[u].append(l)
    order = sorted(links_of)
    schedule = []
    while any(v > 0 for v in rem.values()):
        if mode == "naive":
            slot = {}
            for u in order:
                cands = [l for l in links_of[u] if rem[l] > 0]
                if cands:
                    slot[u] = min(cands, key=lambda l: (-rem[l], l))
            for l in set(slot.values()):
                rem[l] = max(0, rem[l] - sum(1 for x in slot.values() if x == l))
            schedule.append(slot)
            continue
        pend = {u: sum(rem[l] for l in links_of[u] if len(ps_ends(l, ps_nodes)) == 1)
                for u in order}
        slot = {}
        for u in order:  # pass 1
            cands = []
            for l in links_of[u]:
                if rem[l] <= 0:
                    continue
                ends = ps_ends(l, ps_nodes)
                if len(ends) == 1:
                    cands.append(l)
                else:
                    v = l[0] if l[1] == u else l[1]
                    if (pend[u], u) <= (pend[v], v):
                        cands.append(l)
            if cands:
                l = min(cands, key=lambda l: (-rem[l], l))
                slot[u] = l
                rem[l] -= 1
        for u in order:  # pass 2: idle PSes help
            if u in slot:
                continue
            cands = [l for l in links_of[u] if rem[l] > 0]
            if cands:
                l = min(cands, key=lambda l: (-rem[l], l))
                slot[u] = l
                rem[l] -= 1
        assert slot, "greedy made no progress"
        schedule.append(slot)
    return schedule
