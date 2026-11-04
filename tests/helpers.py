import numpy as np
from topology import assign_initial_ps, generate_network, generate_requests


def make_instance(seed, n=30, gamma=0.5, beta=0.3, nps=4, nreq=10):
    rng = np.random.default_rng(seed)
    G = generate_network(n, gamma, beta, rng)
    return G, assign_initial_ps(G, nps, rng), generate_requests(G, nreq, rng)
