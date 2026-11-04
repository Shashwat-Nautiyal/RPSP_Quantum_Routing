# Replication notes (honest status)

## What was actually run (single CPU core, tiny samples)
* `python run_tests.py`: all tests pass (incl. Fig. 1: 7 / 5 / 3 slots).
* Debug run (5 trials, 20-60 nodes): `results_debug/` (made before the `RPD+GD-naive` scheme existed).
* Default-scale run (120 nodes, 15 PSes, 100 requests, 3 trials per point; gamma=1.3; requests=200):
  `results_default_scale/` (REPORT.md, fig3.png, fig4.png). **n = 2-3 trials per point: indicative only,
  no meaningful confidence intervals.** One requests=200 trial hit the 60 s LP limit in APSP and is
  reported as `timeout` (skipped, not treated as infeasible).
* The full 100-trial x all-sweeps replication was NOT run. Do it with `experiments.py run ...` (README).

## Indicative default-scale results (paired savings, %)
| comparison | gamma=1.3 | 15 initial PS | 200 requests | paper |
|---|---|---|---|---|
| APSP vs RAS (added PSes) | 85.5 | 61.3 | 61.4 | up to 98.33 |
| APSP vs SPS | 79.1 | 52.5 | 58.5 | up to 98.13 |
| RPSP vs SP+PSP (slots) | 27.6 | 20.3 | 41.4 | up to 46 (27.09 at 200 req) |
| RPSP vs RPD+GD (slots) | 0.0 | 0.0 | 0.0 | up to 51 (43.76 at 200 req) |
| RPSP vs RPD+GD-naive | 10.1 | 4.9 | 3.6 | - |

## Discrepancies and likely causes
1. **RPD+GD gap missing.** The D4 greedy (coordinated) matches PSP here; the paper's GD sentence is truncated.
   The uncoordinated variant opens a 4-10% gap, still far below the paper's. The paper's GD is probably weaker still.
2. **Placement savings below 98%.** Topology: the stated Waxman defaults never connect (see DECISIONS.md), so
   beta was raised by a fallback; the paper's actual graphs are unknown. Savings also grow with density
   (79-86% at gamma=1.3 vs 52-61% at gamma=0.35), consistent with the paper's trend.
3. **Unspecified k, tie-breaking, shortest-path metric** (D1, D2) affect SP+PSP and RPD.
4. The paper quotes inconsistent headline numbers (87/36 abstract; 98.33/98.13 and 36/26 findings; 51/46 Sec. V-C).
