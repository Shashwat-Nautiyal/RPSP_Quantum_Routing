import numpy as np
from unittest import mock
import solver
from baselines import ras, sps
from placement import (PlacementModel, apsp, redundant_additions, solve_ilp_placement)
from solver import SolveResult, SolverTimeout, TIMEOUT, require_decision
from topology import is_feasible, light_subgraph
from tests.helpers import make_instance


def test_ras_lights_every_link():
    G, ps, req = make_instance(1)
    final = set(ps) | set(ras(G, ps))
    assert light_subgraph(G, final).number_of_edges() == G.number_of_edges()


def test_sps_makes_feasible():
    G, ps, req = make_instance(2)
    assert is_feasible(G, set(ps) | set(sps(G, ps, req)), req)


def test_apsp_feasible_and_not_worse_than_baselines_in_aggregate():
    tot = {"apsp": 0, "ras": 0, "sps": 0}
    for seed in range(8):
        G, ps, req = make_instance(seed, n=40, nps=4, nreq=15)
        r = apsp(G, req, ps)
        assert is_feasible(G, r.ps_final, req)
        assert set(ps) <= set(r.ps_final) and len(r.added) == len(r.ps_final) - len(ps)
        tot["apsp"] += len(r.added); tot["ras"] += len(ras(G, ps)); tot["sps"] += len(sps(G, ps, req))
    assert tot["apsp"] <= tot["ras"] and tot["apsp"] <= tot["sps"], tot


def test_apsp_vs_exact_ilp_small_dense():
    gaps = []
    for seed in range(6):
        G, ps, req = make_instance(seed, n=14, gamma=0.9, beta=0.4, nps=1, nreq=8)
        a = apsp(G, req, ps)
        e = solve_ilp_placement(G, req, ps, time_limit=60)
        assert e.status == "optimal"
        assert is_feasible(G, e.ps_final, req)
        assert len(a.added) >= len(e.added)       # heuristic >= optimum
        gaps.append(len(a.added) - len(e.added))
    assert np.mean(gaps) <= 1.5, gaps             # and the gap is small


def test_relaxed_lp_lower_bounds_ilp():
    G, ps, req = make_instance(3, n=14, gamma=0.9, beta=0.4, nps=1, nreq=8)
    m = PlacementModel(G, req, ps)
    lp = m.solve_relaxed().obj
    ilp = m.solve_exact().obj
    assert lp <= ilp + 1e-6


def test_fix_is_incremental():
    G, ps, req = make_instance(4, n=14, gamma=0.9, beta=0.4, nps=1, nreq=6)
    m = PlacementModel(G, req, ps)
    A = m.model.A_ub
    m.fix(5)
    assert m.model.A_ub is A and m.model.lb[5] == 1.0


def test_timeout_is_not_infeasible():
    """Rule 3: a time-limit stop maps to 'timeout' and require_decision aborts."""
    fake = mock.Mock(status=1, x=None, fun=None)
    G, ps, req = make_instance(5, n=14, gamma=0.9, beta=0.4, nps=1, nreq=4)
    m = PlacementModel(G, req, ps)
    with mock.patch.object(solver, "linprog", return_value=fake):
        res = solver.solve_model(m.model, 1.0)
    assert res.status == TIMEOUT
    try:
        require_decision(res)
    except SolverTimeout:
        return
    raise AssertionError("timeout must raise")


def test_redundancy_report_runs():
    G, ps, req = make_instance(6, n=30, nps=2, nreq=10)
    r = apsp(G, req, ps)
    red = redundant_additions(G, req, ps, r.added)
    assert set(red) <= set(r.added)


def test_apsp_batch_mode_feasible():
    G, ps, req = make_instance(7, n=40, nps=3, nreq=15)
    r = apsp(G, req, ps, batch_size=3)
    assert is_feasible(G, r.ps_final, req)
