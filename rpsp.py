"""Task 4.8 / 5.1 / 5.2: full RPSP pipeline and the timing baselines."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from baselines import shortest_light_paths
from placement import PlacementResult, apsp
from provisioning import (greedy_provisioning, link_demands, psp, schedule_from_p,
                          verify_schedule)
from routing import candidate_paths, rpd


@dataclass
class RPSPResult:
    ps_final: frozenset
    added: list
    paths: list  # chosen node tuple per request
    T: int
    T_lp_routing: int
    timings: dict = field(default_factory=dict)
    psp_result: object = None


def run_sp_psp(G, ps_final, requests, time_limit=60.0, backend="highs"):
    """Task 5.1: shortest light path per request, then PSP."""
    paths = shortest_light_paths(G, ps_final, requests)
    res = psp(link_demands(paths, ps_final), ps_final, time_limit, backend)
    return paths, res


def run_rpd_gd(chosen_paths, ps_final, mode="coordinated"):
    """Task 5.2: RPD paths + greedy provisioning.  Returns (T, schedule)."""
    sched = greedy_provisioning(link_demands(chosen_paths, ps_final), ps_final, mode)
    return len(sched), sched


def run_rpsp(G, initial_ps, requests, k=3, backend="highs", lp_time_limit=60.0,
             batch_size=1, forbid_per_iter=1, placement: PlacementResult | None = None,
             upper_hint=None, verify=False) -> RPSPResult:
    """APSP -> candidate paths -> RPD -> PSP."""
    tm = {}
    t = time.time()
    pl = placement or apsp(G, requests, initial_ps, lp_time_limit, backend, batch_size)
    tm["apsp"] = time.time() - t
    t = time.time()
    cands = candidate_paths(G, pl.ps_final, requests, k)
    tm["candidates"] = time.time() - t
    t = time.time()
    rd = rpd(cands, pl.ps_final, upper_hint, forbid_per_iter, time_limit=lp_time_limit,
             backend=backend)
    chosen = [cands[i][j] for i, j in enumerate(rd.chosen)]
    tm["rpd"] = time.time() - t
    t = time.time()
    pr = psp(link_demands(chosen, pl.ps_final), pl.ps_final, lp_time_limit, backend)
    tm["psp"] = time.time() - t
    if verify:
        _, mk = verify_schedule(chosen, pl.ps_final, schedule_from_p(pr.p))
        assert mk <= pr.T
    return RPSPResult(pl.ps_final, pl.added, chosen, pr.T, rd.T_lp, tm, pr)
