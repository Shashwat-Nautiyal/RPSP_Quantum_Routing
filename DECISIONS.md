# DECISIONS.md - choices the paper leaves open (Phase 0)

All choices are applied identically to every scheme.

| # | Question | Decision |
|---|----------|----------|
| D1 | "Shortest path" | Fewest hops; ties by total km; then lexicographically smallest node-id sequence (`topology.shortest_path`). Yen uses weight `1e7 + km`, which is hop-dominant. |
| D2 | Candidate paths *k* | `k = 3` (`--k`). Sensitivity sweep `k in {1,3,5}` available as `--sweeps k`. k=1 must make RPSP == SP+PSP (it does: sanity check). |
| D3 | Yen on full graph or light subgraph | Light subgraph of the **final** PS set (`routing.candidate_paths`). Candidate 0 is forced to equal the D1 shortest path. |
| D4 | Greedy provisioning (GD) | As proposed: every slot each PS serves its adjacent link with the most remaining unmet demand; a two-PS-end link is "owned" by the end with smaller pending one-end load (ties: id); a PS left idle helps on any adjacent link with demand. **Extra, not a replacement:** `RPD+GD-naive` (uncoordinated, no ownership) is reported as a D4 sensitivity because the paper's one-sentence description is truncated and the coordinated rule turned out to be almost as good as PSP (see REPLICATION_NOTES.md). |
| D5 | Potential requests vs. batch | Same request set for placement and for routing/scheduling. |
| D6 | Small-N / default-parameter connectivity | **Amended after measurement (below).** Up to 200 plain rejection samples with the requested (gamma, beta); if none connects, raise beta by x1.25 per level (50 samples per level) until connected; gamma is never changed. The beta actually used is stored per trial (`beta_used`) and listed in the report. `--beta-fallback skip` restores the original "skip and count" rule (trials are then reported as `disconnected`). |
| D7 | Request sampling | s != d, pairs may repeat, repeats are distinct requests. Requests with equal unordered (s,d) are merged only inside the Problem (1) LP (exact reduction: identical constraints). |
| D8 | Horizon for Problem (3) | Search `[1, hi]`, `hi` = SP+PSP result (always LP-feasible since candidate 0 is the shortest path); if forbidding makes `hi` infeasible the horizon is doubled up to `cap = #requests x max path length`. |
| D9 | Time-indexed vs aggregated Problem (3) | **Added.** Problem (3) at fixed T only depends on the final state (constraints (2e),(3h)) and a unit per-slot PS capacity, so with `X = sum_t x` it is *exactly* equivalent to a small LP (`routing.build_problem3(time_indexed=False)`; derivation in the docstring). A feasible aggregated point is spread evenly over the T slots. The literal x/y/z/w model (`time_indexed=True`) is implemented and `tests/test_routing.py::test_aggregated_equals_time_indexed_feasibility` checks equal feasibility for all T on random instances. Experiments use the aggregated model (about 100x smaller). |

## Measured connectivity of the paper's default generator (Task 1.2)

200-sample estimates (gamma = 0.35), `python experiments.py connectivity`:

| N | beta=0.10 | 0.15 | 0.20 | 0.30 | 0.60 |
|---|-----------|------|------|------|------|
| 20  | 0% (deg 0.4) | 0% (0.8) | 0% (1.1) | 3% (1.9) | 58% (3.2) |
| 60  | 0% (1.4) | 2% (2.7) | 17% (3.9) | 83% (6.3) | 100% |
| 120 | **0%** (3.0) | 57% (5.8) | 95% (8.3) | 100% | 100% |
| 200 | 22% (5.3) | 92% (9.8) | 100% | 100% | 100% |

So with the paper's stated formula and defaults, **no connected 120-node graph is obtained in practice** (mean degree about 3, not about 4 as the task list guessed; N=20 needs beta of about 0.6). That is why the fallback exists. Consequences: (i) instances are denser than "gamma=0.35, beta=0.1" suggests, (ii) beta_used is not constant across a sweep (larger for small N). Both are reported; both are plausible sources of quantitative differences to the paper.
