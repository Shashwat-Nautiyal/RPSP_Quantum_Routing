"""Baselines.  Placement: RAS, SPS (Phase 2).  Timing: SP+PSP, RPD+GD (Phase 5)."""
from __future__ import annotations

import networkx as nx

from topology import light_subgraph, link_key, path_links, shortest_path


def _higher_degree_end(G, a, b):
    """Higher-degree end of a link; tie -> smaller node id."""
    return min((a, b), key=lambda n: (-G.degree(n), n))


def ras(G: nx.Graph, initial_ps) -> list[int]:
    """Task 2.1: make every link light.  Request-independent.

    Links are processed in sorted order; adding a PS never darkens a link, so one pass
    is equivalent to 'while a dark link exists'.
    """
    ps = set(initial_ps)
    added = []
    for u, v in sorted(link_key(a, b) for a, b in G.edges):
        if u not in ps and v not in ps:
            w = _higher_degree_end(G, u, v)
            ps.add(w)
            added.append(w)
    return added


def sps(G: nx.Graph, initial_ps, requests) -> list[int]:
    """Task 2.2: shortest path (D1) per request in the FULL graph; light up dark links."""
    ps = set(initial_ps)
    added = []
    for s, d in requests:
        path = shortest_path(G, s, d)
        for u, v in path_links(path):
            if u not in ps and v not in ps:
                w = _higher_degree_end(G, u, v)
                ps.add(w)
                added.append(w)
    return added


def shortest_light_paths(G, ps_final, requests):
    """SP+PSP routing (Task 5.1): D1 shortest path in the light subgraph (D3)."""
    Gl = light_subgraph(G, ps_final)
    cache, out = {}, []
    for s, d in requests:
        if (s, d) not in cache:
            p = shortest_path(Gl, s, d)
            assert p is not None, "request infeasible in light subgraph"
            cache[(s, d)] = p
        out.append(cache[(s, d)])
    return out
