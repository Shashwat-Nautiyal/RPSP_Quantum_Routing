"""The 9-node motivation example of Fig. 1 (Task 5.3).

Topology is reconstructed from the figure (the edge list is read off the drawing, so a
couple of dark links such as A-F, F-G, D-H may differ from the original; they do not
influence any relay path because dark links are never used).
Nodes A..I = 0..8.  PS nodes: B, D, E, I.
"""
import networkx as nx

NAMES = "ABCDEFGHI"
ID = {n: i for i, n in enumerate(NAMES)}
PS_NODES = frozenset(ID[x] for x in "BDEI")
EDGES = ["AB", "AF", "BC", "BD", "BE", "CD", "DE", "DH", "EF", "EG", "EH", "EI", "FG", "GI", "HI"]
REQUESTS = [(ID["A"], ID["I"]), (ID["C"], ID["G"]), (ID["F"], ID["H"]), (ID["G"], ID["H"])]


def fig1_graph() -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(range(9))
    for e in EDGES:
        G.add_edge(ID[e[0]], ID[e[1]], km=1.0)
    return G


def p(s):  # "ABEI" -> (0,1,4,8)
    return tuple(ID[c] for c in s)


# relay paths of the three sub-figures
PATHS_AB = [p("ABEI"), p("CBEG"), p("FEH"), p("GEH")]   # Fig. 1(a)/(b): all via E
PATHS_C = [p("ABEI"), p("CDEG"), p("FEH"), p("GIH")]    # Fig. 1(c): purple bypasses E
# Fig. 1(a) PS provisioning: B-E: one key from E, one from B; E-I from E; rest forced.
P_FIG1A = {(ID["B"], ID["A"]): 1, (ID["B"], ID["C"]): 1, (ID["E"], ID["B"]): 1,
           (ID["B"], ID["E"]): 1, (ID["E"], ID["I"]): 1, (ID["E"], ID["G"]): 2,
           (ID["E"], ID["F"]): 1, (ID["E"], ID["H"]): 2}
