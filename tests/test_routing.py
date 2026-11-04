import numpy as np
from placement import apsp
from provisioning import link_demands, psp, schedule_from_p, verify_schedule
from routing import (build_problem3, candidate_paths, extract_z, min_T, rpd, set_T,
                     solve_problem2_exact)
from solver import OPTIMAL, solve_model
from rpsp import run_sp_psp
from topology import is_feasible, path_links
from tests.helpers import make_instance


def _small(seed, nreq=4, k=2):
    G, ps, req = make_instance(seed, n=10, gamma=0.8, beta=0.5, nps=2, nreq=nreq)
    pl = apsp(G, req, ps)
    return G, ps, req, pl, candidate_paths(G, pl.ps_final, req, k)


def test_candidate_paths_light_simple_and_sorted():
    G, ps, req, pl, cands = _small(1, nreq=6, k=3)
    for (s, d), pls in zip(req, cands):
        assert 1 <= len(pls) <= 3
        hops = [len(p) for p in pls]
        assert hops == sorted(hops)
        for p in pls:
            assert p[0] == s and p[-1] == d and len(set(p)) == len(p)
            assert all(a in pl.ps_final or b in pl.ps_final for a, b in path_links(p))


def test_aggregated_equals_time_indexed_feasibility():
    """Decision D9: aggregated LP == literal Problem (3) for every T."""
    for seed in range(4):
        G, ps, req, pl, cands = _small(seed)
        agg = build_problem3(cands, pl.ps_final)
        for T in range(1, 7):
            set_T(agg, T)
            a = solve_model(agg).status == OPTIMAL
            full = build_problem3(cands, pl.ps_final, T, time_indexed=True)
            f = solve_model(full).status == OPTIMAL
            assert a == f, (seed, T, a, f)


def test_min_T_matches_continuous_bound():
    G, ps, req, pl, cands = _small(2, nreq=6)
    m = build_problem3(cands, pl.ps_final)
    T, _ = min_T(m, 1, 50, 100)
    set_T(m, T - 1) if T > 1 else None
    assert T == 1 or solve_model(m).status != OPTIMAL     # T-1 infeasible
    set_T(m, T)
    assert solve_model(m).status == OPTIMAL                # T feasible


def test_rpd_integral_and_one_path_per_request():
    for seed in range(5):
        G, ps, req = make_instance(seed, n=40, nps=5, nreq=20)
        pl = apsp(G, req, ps)
        cands = candidate_paths(G, pl.ps_final, req, 3)
        r = rpd(cands, pl.ps_final)
        assert len(r.chosen) == len(req)
        chosen = [cands[i][j] for i, j in enumerate(r.chosen)]
        res = psp(link_demands(chosen, pl.ps_final), pl.ps_final)
        done, mk = verify_schedule(chosen, pl.ps_final, schedule_from_p(res.p))
        assert mk <= res.T and max(done) == mk
        # LP routing bound is a lower bound on what PSP achieves, and PSP <= 2x it
        assert r.T_lp <= res.T <= 2 * r.T_lp + 1


def test_rpd_not_worse_than_sp_psp_lp_bound():
    for seed in range(5):
        G, ps, req = make_instance(seed + 10, n=40, nps=5, nreq=20)
        pl = apsp(G, req, ps)
        _, sp_res = run_sp_psp(G, pl.ps_final, req)
        cands = candidate_paths(G, pl.ps_final, req, 3)
        r = rpd(cands, pl.ps_final, upper_hint=sp_res.T)
        assert r.T_lp <= sp_res.T          # LP optimum over a superset of the SP routing


def test_rpd_forbid_multiple_terminates():
    G, ps, req = make_instance(21, n=40, nps=5, nreq=20)
    pl = apsp(G, req, ps)
    cands = candidate_paths(G, pl.ps_final, req, 3)
    r = rpd(cands, pl.ps_final, forbid_per_iter=5)
    assert len(r.chosen) == 20


def test_pipeline_vs_exact_problem2_tiny():
    """Task 5.3: tiny instances (<=8 nodes, <=4 requests): exact optimum <= pipeline T,
    and PSP on the same paths is within 2x of the exact provisioning optimum."""
    ratios = []
    for seed in range(6):
        G, ps, req = make_instance(seed, n=8, gamma=0.9, beta=0.5, nps=2, nreq=4)
        pl = apsp(G, req, ps)
        cands = candidate_paths(G, pl.ps_final, req, 2)
        r = rpd(cands, pl.ps_final)
        chosen = [cands[i][j] for i, j in enumerate(r.chosen)]
        res = psp(link_demands(chosen, pl.ps_final), pl.ps_final)
        t_joint = solve_problem2_exact(cands, pl.ps_final, T_max=res.T)
        assert t_joint is not None and t_joint <= res.T
        t_fixed = solve_problem2_exact([[p] for p in chosen], pl.ps_final, T_max=res.T)
        assert t_fixed is not None and t_fixed <= res.T <= 2 * t_fixed
        ratios.append(res.T / t_joint)
    assert max(ratios) <= 2.0, ratios
