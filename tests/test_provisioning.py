import numpy as np
from fig1_example import (ID, P_FIG1A, PATHS_AB, PATHS_C, PS_NODES, REQUESTS, fig1_graph)
from placement import apsp
from provisioning import (greedy_provisioning, link_demands, psp, schedule_from_p,
                          verify_schedule)
from rpsp import run_rpsp, run_sp_psp
from topology import link_key


def _sched_T(paths, p):
    done, mk = verify_schedule(paths, PS_NODES, schedule_from_p(p))
    return mk


def fig1_report(out=print):
    r_a = _sched_T(PATHS_AB, P_FIG1A)
    r_b = psp(link_demands(PATHS_AB, PS_NODES), PS_NODES).T
    r_c = psp(link_demands(PATHS_C, PS_NODES), PS_NODES).T
    G = fig1_graph()
    full = run_rpsp(G, PS_NODES, REQUESTS, k=3, verify=True)
    _, sp = run_sp_psp(G, PS_NODES, REQUESTS)
    out(f"Fig.1(a) hand provisioning : {r_a} slots (paper: 7)")
    out(f"Fig.1(b) PSP, paths via E  : {r_b} slots (paper: 5)")
    out(f"Fig.1(c) PSP, joint paths  : {r_c} slots (paper: 3)")
    out(f"SP+PSP on Fig.1            : {sp.T} slots")
    out(f"RPSP (APSP+RPD+PSP) on Fig.1: {full.T} slots, paths="
        f"{[''.join('ABCDEFGHI'[n] for n in p) for p in full.paths]}")
    return r_a, r_b, r_c, sp.T, full.T


def test_fig1_values():
    r_a, r_b, r_c, sp_T, rpsp_T = fig1_report(lambda *_: None)
    assert (r_a, r_b, r_c) == (7, 5, 3)
    assert sp_T == 5 and rpsp_T == 3


def test_psp_invariants_random():
    rng = np.random.default_rng(0)
    for trial in range(40):
        n = int(rng.integers(5, 12))
        ps = set(rng.choice(n, size=int(rng.integers(2, n)), replace=False).tolist())
        c = {}
        for _ in range(int(rng.integers(3, 25))):
            u, v = rng.choice(n, size=2, replace=False)
            l = link_key(int(u), int(v))
            if l[0] in ps or l[1] in ps:
                c[l] = c.get(l, 0) + int(rng.integers(1, 6))
        if not c:
            continue
        res = psp(c, ps)  # asserts demand, Theorem 2 and ceil(T_lp) inside
        assert res.T >= max(res.load.values())


def test_psp_all_integral_lp_is_optimal():
    # single two-end link with demand 4 -> 2 keys per end
    res = psp({(0, 1): 4}, {0, 1})
    assert res.T == 2


def test_schedule_one_key_per_ps_per_slot():
    res = psp(link_demands(PATHS_C, PS_NODES), PS_NODES)
    for slot in schedule_from_p(res.p):
        assert len(slot) == len(set(slot))   # dict keys: at most one link per PS


def test_greedy_valid_and_not_better_than_lp():
    G = fig1_graph()
    for paths in (PATHS_AB, PATHS_C):
        c = link_demands(paths, PS_NODES)
        sched = greedy_provisioning(c, PS_NODES)
        verify_schedule(paths, PS_NODES, sched)
        assert len(sched) >= psp(c, PS_NODES).T_lp - 1e-9


def test_verify_detects_incomplete_schedule():
    sched = schedule_from_p(psp(link_demands(PATHS_C, PS_NODES), PS_NODES).p)[:-1]
    try:
        verify_schedule(PATHS_C, PS_NODES, sched)
    except AssertionError:
        return
    raise AssertionError("truncated schedule should fail verification")


def test_greedy_naive_valid_and_not_better_than_coordinated_lp():
    for paths in (PATHS_AB, PATHS_C):
        c = link_demands(paths, PS_NODES)
        sched = greedy_provisioning(c, PS_NODES, mode="naive")
        verify_schedule(paths, PS_NODES, sched)
        assert len(sched) >= psp(c, PS_NODES).T_lp - 1e-9
