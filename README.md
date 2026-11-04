# RPSP simulation (Xu, Zhao, Huang, Qiao - INFOCOM 2024)

Python replication of *Routing and Photon Source Provisioning in QKD Networks*:
placement (Problem 1 / APSP), routing (Problem 3 / RPD), provisioning (Problems 4-5 / PSP),
baselines (RAS, SPS, SP+PSP, RPD+GD), a Fig. 3 / Fig. 4 experiment harness, and tests.
Phase 6 (extension) is intentionally **not** implemented (the task list says to wait for a choice).

## Quick start
```bash
pip install -r requirements.txt
python run_tests.py                      # or: pytest   (30+ tests, ~15 s)
python experiments.py validate           # Fig. 1 example: 7 / 5 / 3 slots
python experiments.py connectivity       # measured connection rates (Task 1.2)
python experiments.py run --debug --out results_debug          # smoke run, ~1 min
python experiments.py run --sweeps nodes requests gamma initial_ps k \
       --trials 100 --jobs 8 --out results --resume            # full replication
python plots.py --raw results --out results                    # fig3.png fig4.png REPORT.md
```
Useful flags: `--figs 3` / `--figs 4`, `--ilp` (exact ILP where the paper says it is tractable),
`--batch-size m` (APSP adds m PSes per LP solve; 1 = paper), `--forbid-per-iter m` (RPD),
`--backend pulp` (CBC cross-check), `--beta-fallback skip`.

## Layout
| file | content |
|---|---|
| `solver.py` | one swappable LP/ILP backend (HiGHS via scipy; PuLP/CBC optional), status = optimal / infeasible / timeout / error, `SolverTimeout` |
| `topology.py` | Waxman generator (explicit gamma/beta -> networkx mapping), initial PS, requests, `light_subgraph`, `is_feasible`, `link_key`, D1 shortest path |
| `placement.py` | Problem (1) model (built once, `fix(u)` incremental), exact ILP, **APSP (Alg. 1)** |
| `routing.py` | candidate paths (Yen, light subgraph), Problem (3) builders (literal and exact aggregated), binary search for T*, **RPD (Alg. 2)**, exact Problem (2) for tiny cases |
| `provisioning.py` | link demand, **PSP (Alg. 3)** with the fixes below, schedule builder, `verify_schedule`, greedy GD |
| `baselines.py` | RAS, SPS, shortest light paths |
| `rpsp.py` | `run_rpsp` (APSP -> RPD -> PSP), `run_sp_psp`, `run_rpd_gd` |
| `fig1_example.py` | the 9-node motivation example |
| `experiments.py` | paired trials, joblib parallelism, raw CSV, resume, debug mode, progress logs |
| `plots.py` | aggregation (mean, s.e.), paired savings, Fig. 3/4 replicas, `REPORT.md` |
| `tests/`, `run_tests.py` | unit / validation tests (pytest-style, runnable without pytest) |
| `DECISIONS.md` | D1-D9 and the connectivity measurement |
| `REPLICATION_NOTES.md` | what was run here, results, discrepancies vs. the paper |

## Paper issues fixed (as listed in the task list)
* Alg. 2: F is updated; argmin ranges over fractional, non-forbidden paths; exactly one path kept per request; a request's last path is fixed instead of forbidden.
* Alg. 3: line 7 no longer double-counts the floors (uses updated `m_u`); the rounding loop runs over `B - C` only.
* (2f): implemented as "nothing distributed before slot 1" (no variable for t=0).
* APSP's loop condition is an integral BFS feasibility test (the relaxed LP is almost always feasible).
* Timeouts are never treated as infeasible (`SolverTimeout`, trial row gets status `timeout`).

## Verification built in
Fig. 1 example (7/5/3 slots; RPSP finds the 3-slot routing), PSP assertions on every call
(demand conservation, `ceil(T_LP) <= T <= 2 T_LP`, Theorem 2), a slot-level schedule simulator
(`verify_schedule`) run in tests and on every `verify_every`-th trial, aggregated-vs-literal
Problem (3) equivalence, APSP vs exact ILP, PSP vs exact Problem (2) on tiny instances, and
a statistical test that the generator follows `gamma * exp(-l / (beta L))` (and would reject a swapped mapping).

## Caveats
* `pulp` was not installable in the sandbox used to build this (offline), so the PuLP/CBC backend
  (`solver._solve_pulp`) is **written but unexercised**; all runs/tests used HiGHS (`milp` for ILPs).
  Run `python experiments.py run --debug --backend pulp` once to check it on your machine.
* Fig. 1's edge list was read from the drawing; only light links matter for the example.
* Runtime: one default-size trial (120 nodes, 100 requests) costs about 0.5-1 min, dominated by the
  APSP LP loop (about 25 solves of a ~50k-variable LP). The full 100-trial x ~35-point replication is
  therefore on the order of 1-2 CPU-days; use `--jobs`, `--batch-size 3`, or fewer trials.
