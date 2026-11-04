from experiments import SWEEPS, TrialConfig, run_trial, trial_seed


def _params():
    return dict(num_nodes=25, num_ps=3, num_requests=8, gamma=0.5, beta=0.3, k=3)


def test_trial_paired_and_deterministic():
    cfg = TrialConfig(verify_every=1)
    seed = trial_seed(1, "nodes", 0, 0)
    a = run_trial("nodes", 25, 0, _params(), seed, cfg)
    b = run_trial("nodes", 25, 0, _params(), seed, cfg)
    key = lambda rows: sorted((r["scheme"], r["status"], r["added_ps"], r["T"]) for r in rows)  # noqa
    assert key(a) == key(b)
    schemes = {r["scheme"] for r in a}
    assert {"RAS", "SPS", "RPSP-APSP", "SP+PSP", "RPSP", "RPD+GD"} <= schemes
    assert all(r["status"] == "ok" for r in a), [r for r in a if r["status"] != "ok"]
    byname = {r["scheme"]: r for r in a}
    assert byname["RPSP-APSP"]["added_ps"] <= byname["RAS"]["added_ps"]
    assert byname["RPSP"]["T"] <= 2 * byname["SP+PSP"]["T"]


def test_seeds_differ_across_trials():
    assert trial_seed(1, "nodes", 0, 0) != trial_seed(1, "nodes", 0, 1)
    assert set(SWEEPS) >= {"nodes", "requests", "gamma", "initial_ps"}
