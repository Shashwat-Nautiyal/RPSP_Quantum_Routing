"""Task 5.5-5.7: aggregate raw CSVs, draw Fig. 3 / Fig. 4 replicas, savings table, report."""
from __future__ import annotations

import argparse
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

FIG3 = ("RAS", "SPS", "RPSP-APSP", "RPSP-ILP")
FIG4 = ("RPD+GD", "RPD+GD-naive", "SP+PSP", "RPSP")
SWEEP_ORDER = ["nodes", "requests", "gamma", "initial_ps"]
XLABEL = {"nodes": "Number of nodes", "requests": "Number of QKD requests",
          "gamma": "Network connectivity (gamma in Waxman model)",
          "initial_ps": "Number of PS nodes at the beginning", "k": "k (candidate paths)"}
STYLE = {"RAS": ("tab:blue", "o"), "SPS": ("tab:red", "s"), "RPSP-APSP": ("black", "o"),
         "RPSP-ILP": ("magenta", "x"), "RPD+GD": ("tab:blue", "o"), "RPD+GD-naive": ("tab:green", "^"), "SP+PSP": ("tab:red", "s"),
         "RPSP": ("black", "o")}
# (baseline, metric, what the paper says)
PAPER = {
    ("fig3", "RAS"): "up to 98.33% (gamma=1.3); 89% over node sweep; abstract: 87%",
    ("fig3", "SPS"): "up to 98.13% (gamma=1.3); 93% over node sweep",
    ("fig4", "RPD+GD"): "up to 51% (node sweep); 43.76% at 200 requests; abstract: 36%",
    ("fig4", "SP+PSP"): "up to 46% (node sweep); 27.09% at 200 requests; 26% in summary",
}


def load(raw_dir):
    files = sorted(glob.glob(os.path.join(raw_dir, "raw_*.csv")))
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True) if files else pd.DataFrame()


def aggregate(df, schemes, metric):
    d = df[df.scheme.isin(schemes)]
    ok = d[d.status == "ok"]
    g = ok.groupby(["sweep", "value", "scheme"])[metric]
    out = g.agg(mean="mean", sem=lambda x: x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0,
                n_ok="count").reset_index()
    bad = d[d.status != "ok"].groupby(["sweep", "value", "scheme"]).size().rename("n_not_ok")
    out = out.merge(bad.reset_index(), how="left", on=["sweep", "value", "scheme"])
    out["n_not_ok"] = out["n_not_ok"].fillna(0).astype(int)
    return out


def savings(df, ours, baselines, metric):
    """Paired savings: 1 - mean(ours)/mean(baseline) over trials where both succeeded."""
    rows = []
    for (sw, val), grp in df.groupby(["sweep", "value"]):
        piv = grp[grp.status == "ok"].pivot_table(index="trial", columns="scheme", values=metric)
        for b in baselines:
            if ours in piv and b in piv:
                both = piv[[ours, b]].dropna()
                if len(both) and both[b].mean() > 0:
                    rows.append(dict(sweep=sw, value=val, baseline=b, n_paired=len(both),
                                     saving_pct=100 * (1 - both[ours].mean() / both[b].mean())))
    return pd.DataFrame(rows)


def draw(agg, schemes, ylabel, title, path):
    sweeps = [s for s in SWEEP_ORDER if s in set(agg.sweep)]
    fig, axes = plt.subplots(1, max(1, len(sweeps)), figsize=(4.2 * max(1, len(sweeps)), 3.4),
                             squeeze=False)
    for ax, sw in zip(axes[0], sweeps):
        for s in schemes:
            a = agg[(agg.sweep == sw) & (agg.scheme == s)].sort_values("value")
            if len(a):
                c, m = STYLE[s]
                ax.errorbar(a.value, a["mean"], yerr=1.96 * a["sem"], color=c, marker=m, ms=4,
                            lw=1, capsize=2, label=s)
        ax.set_xlabel(XLABEL[sw]); ax.set_ylabel(ylabel); ax.grid(alpha=.3); ax.legend(fontsize=7)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def report(raw_dir, out_dir):
    df = load(raw_dir)
    if df.empty:
        raise SystemExit(f"no raw_*.csv in {raw_dir}")
    os.makedirs(out_dir, exist_ok=True)
    inst = df[df.scheme == "_instance"]
    md = ["# Replication report (auto-generated)\n"]
    md.append("## Instances\n")
    md.append(inst.groupby("sweep").status.value_counts().unstack(fill_value=0).to_markdown() + "\n")
    bu = inst[inst.status == "ok"].groupby(["sweep", "value"]).beta_used.agg(["mean", "min", "max"])
    md.append("beta actually used by the generator (D6 fallback):\n\n" + bu.round(3).to_markdown() + "\n")
    tabs = {}
    for name, schemes, metric, ylabel in (("fig3", FIG3, "added_ps", "Number of PSes to be added"),
                                          ("fig4", FIG4, "T", "Number of time slots")):
        d = df[df.sweep.isin(SWEEP_ORDER)]
        a = aggregate(d, schemes, metric)
        if a.empty:
            continue
        a.to_csv(os.path.join(out_dir, f"summary_{name}.csv"), index=False)
        draw(a, schemes, ylabel, f"{name.replace('fig', 'Fig. ')} replica (mean, 95% CI)",
             os.path.join(out_dir, f"{name}.png"))
        ours = "RPSP-APSP" if name == "fig3" else "RPSP"
        base = ("RAS", "SPS") if name == "fig3" else ("RPD+GD", "RPD+GD-naive", "SP+PSP")
        s = savings(d, ours, base, metric)
        s.to_csv(os.path.join(out_dir, f"savings_{name}.csv"), index=False)
        tabs[name] = s
        md.append(f"## {name.upper()} - paired savings of {ours} (%)\n")
        md.append(s.round(2).to_markdown(index=False) + "\n")
        md.append(f"non-ok (timeout/error/skipped) rows: {int(a.n_not_ok.sum())}\n")
    ksw = df[(df.sweep == "k") & (df.status == "ok") & df.scheme.isin(FIG4)]
    if len(ksw):
        md.append("## Sensitivity to k (D2), mean time slots\n")
        md.append(ksw.pivot_table(index="value", columns="scheme", values="T").round(2).to_markdown() + "\n")
    md.append("## Replication vs. paper\n")
    md.append("| comparison | this run: max saving over all sweeps (where) | paper |\n|---|---|---|\n")
    for (fig, b), txt in PAPER.items():
        s = tabs.get(fig)
        if s is not None and len(s[s.baseline == b]):
            r = s[s.baseline == b].sort_values("saving_pct").iloc[-1]
            mine = f"{r.saving_pct:.1f}% ({r.sweep}={r.value})"
        else:
            mine = "n/a"
        md.append(f"| {fig} RPSP vs {b} | {mine} | {txt} |\n")
    md.append("\nThe paper itself quotes different headline numbers in the abstract (87% / 36%), "
              "the findings list (98.33% / 98.13%, 36% / 26%) and Sec. V-C (51% / 46%), so no single "
              "'target' exists. Discrepancy notes are in REPLICATION_NOTES.md.\n")
    with open(os.path.join(out_dir, "REPORT.md"), "w") as f:
        f.write("\n".join(md))
    print(f"wrote {out_dir}/REPORT.md, fig3.png, fig4.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="results")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    report(a.raw, a.out)
