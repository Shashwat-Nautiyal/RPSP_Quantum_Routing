import math
import numpy as np
import pytest_compat as pc  # noqa: F401  (tiny shim, see run_tests.py)
import networkx as nx
from topology import (DisconnectedError, assign_initial_ps, generate_network, generate_requests,
                      is_feasible, light_subgraph, link_key, shortest_path, waxman_raw,
                      waxman_link_probability)


def _expected(G, gamma, beta):
    pos = np.array([G.nodes[i]["pos"] for i in G.nodes])
    D = np.linalg.norm(pos[:, None] - pos[None], axis=2)
    L = D.max()
    iu = np.triu_indices(len(pos), 1)
    p = waxman_link_probability(D[iu], L, gamma, beta)
    return p.sum(), (p * (1 - p)).sum()


def test_waxman_matches_paper_formula():
    """Empirical link count agrees with P = gamma*exp(-l/(beta L)); the swapped
    (gamma<->beta) mapping would be rejected by the same test."""
    rng = np.random.default_rng(0)
    gamma, beta = 0.9, 0.15
    obs = exp_ = var = exp_sw = 0.0
    for _ in range(300):
        G = waxman_raw(25, gamma, beta, rng)
        e, v = _expected(G, gamma, beta)
        exp_ += e
        var += v
        obs += G.number_of_edges()
        exp_sw += _expected(G, beta, gamma)[0]  # what a swapped mapping would predict
    z = (obs - exp_) / math.sqrt(var)
    assert abs(z) < 4, z
    assert abs(obs - exp_sw) / math.sqrt(var) > 10


def test_connected_and_attributes():
    rng = np.random.default_rng(1)
    G = generate_network(40, 0.5, 0.3, rng)
    assert nx.is_connected(G)
    assert all("pos" in G.nodes[n] for n in G) and all(d["km"] > 0 for *_, d in G.edges(data=True))


def test_skip_fallback_raises():
    rng = np.random.default_rng(1)
    try:
        generate_network(20, 0.35, 0.1, rng, max_tries=5, fallback="skip")
    except DisconnectedError:
        return
    raise AssertionError("expected DisconnectedError")


def test_scale_beta_fallback_connects():
    rng = np.random.default_rng(1)
    G = generate_network(20, 0.35, 0.1, rng, max_tries=5)
    assert nx.is_connected(G) and G.graph["beta_used"] > 0.1


def test_requests_and_ps():
    rng = np.random.default_rng(2)
    G = generate_network(30, 0.5, 0.3, rng)
    req = generate_requests(G, 200, rng)
    assert len(req) == 200 and all(s != d for s, d in req)
    assert len(assign_initial_ps(G, 10, rng)) == 10
    assert len(assign_initial_ps(G, 99, rng)) == 30  # clipped
    assert assign_initial_ps(G, 0, rng) == frozenset()


def test_light_subgraph_and_feasibility():
    G = nx.path_graph(4)
    nx.set_edge_attributes(G, 1.0, "km")
    assert is_feasible(G, {1}, [(0, 2)])           # links 0-1,1-2 light
    assert not is_feasible(G, {1}, [(0, 3)])       # 2-3 dark
    assert is_feasible(G, {1, 2}, [(0, 3)])
    assert link_key(3, 1) == (1, 3)
    assert light_subgraph(G, {0}).number_of_edges() == 1


def test_shortest_path_tiebreaks():
    G = nx.Graph()
    G.add_edge(0, 1, km=5.0); G.add_edge(1, 3, km=5.0)   # 10 km
    G.add_edge(0, 2, km=1.0); G.add_edge(2, 3, km=1.0)   # 2 km  -> wins on km
    G.add_edge(0, 4, km=1.0); G.add_edge(4, 3, km=1.0)   # same km, larger id
    assert shortest_path(G, 0, 3) == (0, 2, 3)
    G.add_edge(0, 3, km=100.0)                           # 1 hop wins regardless of km
    assert shortest_path(G, 0, 3) == (0, 3)
