"""Phase 5.4: experiment loop (paired trials, parallel, raw CSV, resume, debug mode)."""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

import baselines
from placement import apsp, solve_ilp_placement
from provisioning import (greedy_provisioning, link_demands, schedule_from_p, verify_schedule)
from rpsp import run_rpd_gd, run_rpsp, run_sp_psp
from solver import SolverTimeout
from topology import (DisconnectedError, assign_initial_ps, connection_stats, generate_network,
                      generate_requests)

log = logging.getLogger("rpsp")

DEFAULTS = dict(num_nodes=120, num_ps=15, num_requests=100, gamma=0.35, beta=0.1, k=3)
SWEEPS = {  # name -> (parameter, values)
    "nodes": ("num_nodes", list(range(20, 201, 20))),
    "requests": ("num_requests", [10, 25, 50, 75, 100, 125, 150, 175, 200]),
    "gamma": ("gamma", [0.35, 0.5, 0.7, 0.9, 1.1, 1.3]),
    "initial_ps": ("num_ps", [0, 5, 10, 15, 20, 25, 30]),
    "k": ("k", [1, 3, 5]),  # D2 sensitivity (Fig. 4 schemes only)
}
SWEEP_ID = {n: i for i, n in enumerate(SWEEPS)}
DEBUG_DEFAULTS = dict(num_nodes=40, num_ps=5, num_requests=20, gamma=0.35, beta=0.1, k=3)
DEBUG_VALUES = {"nodes": [20, 40, 60], "requests": [10, 20, 40], "gamma": [0.35, 0.7, 1.1],
                "initial_ps": [0, 5, 10], "k": [1, 3, 5]}


@dataclass
class TrialConfig:
    fig3: bool = True
    fig4: bool = True
    ilp: bool = False
    ilp_time_limit: float = 60.0
    lp_time_limit: float = 60.0
    batch_size: int = 1
    forbid_per_iter: int = 1
    backend: str = "highs"
    beta_fallback: str = "scale_beta"
    verify_every: int = 10  # verify schedules on every n-th trial (Task 4.7)


def trial_seed(base_seed, sweep, value_idx, trial) -> int:
    return int(np.random.SeedSequence([base_seed, SWEEP_ID[sweep], value_idx, trial])
               .generate_state(1)[0])


def ilp_tractable(p):  # limits quoted in the paper (Sec. IV-A / V-B)
    return p["num_nodes"] < 110 and p["gamma"] >= 0.9 and p["num_requests"] < 140


def run_trial(sweep, value, trial, params, seed, cfg: TrialConfig) -> list[dict]:
    """One paired trial: every scheme sees the identical (G, initial PS, requests)."""
    t_start = time.time()
    base = dict(sweep=sweep, value=value, trial=trial, seed=seed)
    rows = []

    def row(scheme, status="ok", **kw):
        rows.append({**base, "scheme": scheme, "status": status, "added_ps": np.nan,
                     "T": np.nan, "runtime": np.nan, "note": "", **kw})

    rng = np.random.default_rng(seed)
    try:
        G = generate_network(params["num_nodes"], params["gamma"], params["beta"], rng,
                             fallback=cfg.beta_fallback)
    except DisconnectedError as e:
        row("_instance", "disconnected", note=str(e))
        return rows
    base.update(beta_used=G.graph["beta_used"], edges=G.number_of_edges())
    ps0 = assign_initial_ps(G, params["num_ps"], rng)
    req = generate_requests(G, params["num_requests"], rng)
    row("_instance", "ok", note=f"tries={G.graph['tries']}")

    def timed(scheme, fn, metric):
        t = time.time()
        try:
            val, extra = fn()
            row(scheme, runtime=time.time() - t, **{metric: val}, **extra)
            return val
        except SolverTimeout as e:  # rule 3: unknown, trial flagged, never 'infeasible'
            row(scheme, "timeout", runtime=time.time() - t, note=str(e))
        except Exception as e:  # noqa: BLE001 - recorded, never silently dropped
            row(scheme, "error", runtime=time.time() - t, note=repr(e))
        return None

    pl = None
    if cfg.fig3 or cfg.fig4:
        t = time.time()
        try:
            pl = apsp(G, req, ps0, cfg.lp_time_limit, cfg.backend, cfg.batch_size)
        except SolverTimeout as e:
            row("RPSP-APSP", "timeout", runtime=time.time() - t, note=str(e))
        except Exception as e:  # noqa: BLE001
            row("RPSP-APSP", "error", runtime=time.time() - t, note=repr(e))
    if cfg.fig3:
        timed("RAS", lambda: (len(baselines.ras(G, ps0)), {}), "added_ps")
        timed("SPS", lambda: (len(baselines.sps(G, ps0, req)), {}), "added_ps")
        if pl is not None:
            row("RPSP-APSP", runtime=pl.seconds, added_ps=len(pl.added),
                note=f"iters={pl.iterations}")
        if cfg.ilp and ilp_tractable(params):
            def _ilp():
                r = solve_ilp_placement(G, req, ps0, cfg.ilp_time_limit, cfg.backend)
                if r.status != "optimal":
                    raise SolverTimeout(f"ILP {r.status}")
                return len(r.added), {}
            timed("RPSP-ILP", _ilp, "added_ps")
    if cfg.fig4:
        names = ("SP+PSP", "RPSP", "RPD+GD")
        if pl is None:
            for n in names:
                row(n, "skipped_no_placement")
        else:
            do_verify = cfg.verify_every and trial % cfg.verify_every == 0
            sp_res = {}

            def _sp():
                paths, r = run_sp_psp(G, pl.ps_final, req, cfg.lp_time_limit, cfg.backend)
                if do_verify:
                    verify_schedule(paths, pl.ps_final, schedule_from_p(r.p))
                sp_res["T"] = r.T
                return r.T, {}
            timed("SP+PSP", _sp, "T")
            rp = {}

            def _rpsp():
                r = run_rpsp(G, ps0, req, k=params["k"], backend=cfg.backend,
                             lp_time_limit=cfg.lp_time_limit,
                             forbid_per_iter=cfg.forbid_per_iter, placement=pl,
                             upper_hint=sp_res.get("T"), verify=bool(do_verify))
                rp["r"] = r
                return r.T, {"note": f"T_lp={r.T_lp_routing}"}
            timed("RPSP", _rpsp, "T")
            if "r" in rp:
                def _gd():
                    T, sched = run_rpd_gd(rp["r"].paths, pl.ps_final)
                    if do_verify:
                        verify_schedule(rp["r"].paths, pl.ps_final, sched)
                    return T, {}
                timed("RPD+GD", _gd, "T")

                def _gdn():  # extra sensitivity scheme for D4 (uncoordinated greedy)
                    T, sched = run_rpd_gd(rp["r"].paths, pl.ps_final, "naive")
                    if do_verify:
                        verify_schedule(rp["r"].paths, pl.ps_final, sched)
                    return T, {}
                timed("RPD+GD-naive", _gdn, "T")
            else:
                row("RPD+GD", "skipped_no_routing")
    dt = time.time() - t_start
    for r in rows:
        r["trial_seconds"] = dt
        r.setdefault("beta_used", np.nan)
    return rows


def _done_values(path, sweep):
    if not os.path.exists(path):
        return set()
    return set(pd.read_csv(path, usecols=["value"])["value"].unique())


def run_sweep(sweep, values, defaults, n_trials, cfg, out_dir, n_jobs=1, base_seed=2024,
              resume=False):
    from joblib import Parallel, delayed
    param = SWEEPS[sweep][0]
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"raw_{sweep}.csv")
    done = _done_values(out, sweep) if resume else set()
    for vi, value in enumerate(values):
        if value in done:
            log.info("[sweep=%s, value=%s] already done, skipping (resume)", sweep, value)
            continue
        params = {**defaults, param: value}
        jobs = (delayed(run_trial)(sweep, value, tr, params, trial_seed(base_seed, sweep, vi, tr),
                                   cfg) for tr in range(n_trials))
        rows, t0 = [], time.time()
        gen = Parallel(n_jobs=n_jobs, return_as="generator_unordered")(jobs)
        for n, trows in enumerate(gen, 1):
            rows += trows
            log.info("[sweep=%s, value=%s] trial %d/%d done (%.1f s)", sweep, value, n,
                     n_trials, trows[0].get("trial_seconds", float("nan")))
        df = pd.DataFrame(rows).sort_values(["trial", "scheme"])
        bad = df[~df.status.isin(["ok"])]
        log.info("[sweep=%s, value=%s] finished in %.0fs; non-ok rows: %s", sweep, value,
                 time.time() - t0, bad.groupby(["scheme", "status"]).size().to_dict() or "none")
        df.to_csv(out, mode="a", header=not os.path.exists(out), index=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--sweeps", nargs="+", default=["nodes", "requests", "gamma", "initial_ps"],
                   choices=list(SWEEPS))
    r.add_argument("--trials", type=int, default=100)
    r.add_argument("--jobs", type=int, default=1)
    r.add_argument("--out", default="results")
    r.add_argument("--seed", type=int, default=2024)
    r.add_argument("--debug", action="store_true", help="5 trials, small sizes")
    r.add_argument("--figs", nargs="+", type=int, default=[3, 4], choices=[3, 4])
    r.add_argument("--ilp", action="store_true", help="also run exact ILP where tractable")
    r.add_argument("--k", type=int, default=3)
    r.add_argument("--batch-size", type=int, default=1, help="APSP: PSes added per iteration")
    r.add_argument("--forbid-per-iter", type=int, default=1, help="RPD: paths forbidden per iteration")
    r.add_argument("--lp-time-limit", type=float, default=60.0)
    r.add_argument("--backend", default="highs", choices=["highs", "pulp"])
    r.add_argument("--beta-fallback", default="scale_beta", choices=["scale_beta", "skip"])
    r.add_argument("--resume", action="store_true")
    c = sub.add_parser("connectivity")
    c.add_argument("--samples", type=int, default=200)
    sub.add_parser("validate")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", stream=sys.stdout)

    if a.cmd == "connectivity":  # Task 1.2: measure before deciding the fallback
        rng = np.random.default_rng(0)
        for n in (20, 60, 120, 200):
            for beta in (0.1, 0.15, 0.2, 0.3, 0.6):
                rate, deg = connection_stats(n, 0.35, beta, rng, a.samples)
                log.info("N=%d gamma=0.35 beta=%.2f  connected=%.1f%%  mean degree=%.2f",
                         n, beta, 100 * rate, deg)
        return
    if a.cmd == "validate":
        from tests.test_provisioning import fig1_report
        fig1_report(log.info)
        return
    defaults = dict(DEBUG_DEFAULTS if a.debug else DEFAULTS)
    defaults["k"] = a.k
    n_trials = 5 if a.debug else a.trials
    cfg = TrialConfig(fig3=3 in a.figs, fig4=4 in a.figs, ilp=a.ilp, lp_time_limit=a.lp_time_limit,
                      batch_size=a.batch_size, forbid_per_iter=a.forbid_per_iter,
                      backend=a.backend, beta_fallback=a.beta_fallback)
    os.makedirs(a.out, exist_ok=True)
    for sw in a.sweeps:
        values = DEBUG_VALUES[sw] if a.debug else SWEEPS[sw][1]
        run_sweep(sw, values, defaults, n_trials, TrialConfig(**{**cfg.__dict__, **(
            {"fig3": False} if sw == "k" else {})}), a.out, a.jobs, a.seed, a.resume)


if __name__ == "__main__":
    main()
