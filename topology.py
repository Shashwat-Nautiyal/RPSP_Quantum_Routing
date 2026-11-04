"""Phase 1: network generation, initial PS placement, requests, helpers."""
from __future__ import annotations

import heapq
import logging
import math

import networkx as nx
import numpy as np

log = logging.getLogger("rpsp")

AREA_KM = 10_000.0
HOP_W = 1e7  # hop-count-dominant weight for Dijkstra/Yen: w = HOP_W + km  (D1)


class DisconnectedError(RuntimeError):
    pass


# ----------------------------------------------------------------- helpers (Task 1.5)
def link_key(u: int, v: int) -> tuple[int, int]:
    """Canonical undirected link key."""
    return (u, v) if u <= v else (v, u)


def path_links(path) -> list[tuple[int, int]]:
    return [link_key(a, b) for a, b in zip(path[:-1], path[1:])]


def light_subgraph(G: nx.Graph, ps_nodes) -> nx.Graph:
    """Keep only light links (>= 1 PS end).  Keeps all nodes."""
    H = nx.Graph()
    H.add_nodes_from(G.nodes(data=True))
    H.add_edges_from((u, v, dict(d)) for u, v, d in G.edges(data=True)
                     if u in ps_nodes or v in ps_nodes)
    return H


def is_feasible(G: nx.Graph, ps_nodes, requests) -> bool:
    """Integral test: every request has a path in the light subgraph."""
    H = light_subgraph(G, ps_nodes)
    comp = {}
    for ci, nodes in enumerate(nx.connected_components(H)):
        for n in nodes:
            comp[n] = ci
    return all(comp[s] == comp[d] for s, d in requests)


def shortest_path(G: nx.Graph, s: int, d: int):
    """D1: fewest hops; ties by total km; then lexicographically smallest node ids."""
    best = {s: (0, 0.0, (s,))}
    heap = [(0, 0.0, (s,))]
    while heap:
        h, km, path = heapq.heappop(heap)
        u = path[-1]
        if best.get(u) != (h, km, path):
            continue
        if u == d:
            return path
        for v in G.neighbors(u):
            cand = (h + 1, km + G.edges[u, v]["km"], path + (v,))
            if v not in best or cand < best[v]:
                best[v] = cand
                heapq.heappush(heap, cand)
    return None


# ----------------------------------------------------------------- generator (Task 1.2)
def waxman_link_probability(dist, L, gamma, beta):
    """Paper: P(u,v) = gamma * exp(-l(u,v) / (beta * L))."""
    return np.minimum(1.0, gamma * np.exp(-np.asarray(dist) / (beta * L)))


def waxman_raw(num_nodes: int, gamma: float, beta: float, rng: np.random.Generator) -> nx.Graph:
    """One Waxman sample (no connectivity check).

    networkx: p = beta_nx * exp(-d / (alpha_nx * L)).
    paper   : p = gamma    * exp(-l / (beta    * L)).
    => beta_nx = gamma (paper), alpha_nx = beta (paper).   (explicit mapping)
    """
    seed = int(rng.integers(0, 2**31 - 1))
    G = nx.waxman_graph(num_nodes, beta=gamma, alpha=beta, L=None,
                        domain=(0, 0, AREA_KM, AREA_KM), seed=seed)
    for u, v in G.edges:
        (x1, y1), (x2, y2) = G.nodes[u]["pos"], G.nodes[v]["pos"]
        G.edges[u, v]["km"] = math.hypot(x1 - x2, y1 - y2)
    return G


def generate_network(num_nodes: int, gamma: float, beta: float, rng: np.random.Generator,
                     max_tries: int = 200, fallback: str = "scale_beta",
                     beta_scale: float = 1.25, tries_per_level: int = 50,
                     max_levels: int = 60) -> nx.Graph:
    """Connected Waxman network.

    D6: up to `max_tries` plain rejection samples with the requested (gamma, beta).
    fallback='skip'       -> raise DisconnectedError (trial is skipped and counted).
    fallback='scale_beta' -> raise beta by `beta_scale` per level (tries_per_level samples
                             each) until connected; the beta actually used is stored in
                             G.graph['beta_used'] and reported in the raw CSV.
    """
    tries = 0
    for _ in range(max_tries):
        tries += 1
        G = waxman_raw(num_nodes, gamma, beta, rng)
        if nx.is_connected(G):
            G.graph.update(gamma=gamma, beta=beta, beta_used=beta, tries=tries)
            return G
    if fallback == "skip":
        raise DisconnectedError(f"no connected graph in {max_tries} tries (n={num_nodes})")
    b = beta
    for _ in range(max_levels):
        b *= beta_scale
        for _ in range(tries_per_level):
            tries += 1
            G = waxman_raw(num_nodes, gamma, b, rng)
            if nx.is_connected(G):
                G.graph.update(gamma=gamma, beta=beta, beta_used=b, tries=tries)
                return G
    raise DisconnectedError(f"fallback failed (n={num_nodes}, gamma={gamma})")


def connection_stats(num_nodes, gamma, beta, rng, samples=200):
    """Measured connection rate and mean degree of raw samples (Task 1.2)."""
    conn, deg = 0, []
    for _ in range(samples):
        G = waxman_raw(num_nodes, gamma, beta, rng)
        conn += nx.is_connected(G)
        deg.append(2 * G.number_of_edges() / num_nodes)
    return conn / samples, float(np.mean(deg))


def assign_initial_ps(G: nx.Graph, num_ps: int, rng: np.random.Generator) -> frozenset:
    """Task 1.3 / constraint (1c): distinct uniform nodes, clipped to N."""
    n = G.number_of_nodes()
    pick = rng.choice(n, size=min(num_ps, n), replace=False)
    return frozenset(int(x) for x in pick)


def generate_requests(G: nx.Graph, num_requests: int, rng: np.random.Generator):
    """D7: s != d, repeated pairs allowed (distinct requests)."""
    n = G.number_of_nodes()
    s = rng.integers(0, n, size=num_requests)
    d = rng.integers(0, n - 1, size=num_requests)
    d = np.where(d >= s, d + 1, d)
    return [(int(a), int(b)) for a, b in zip(s, d)]
