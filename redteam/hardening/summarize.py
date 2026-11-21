#!/usr/bin/env python3
"""Rank gains of every audited attempt relative to the reproduced reference.

gain = sum_exp weight_exp * sum_metric |coef| * improvement / std, where the
improvement is taken in the metric's better direction and std is the
population standard deviation of that metric over the normalisation cohort.
Two cohorts are reported: every scored attempt (shortcuts and failures
included) and the honest attempts only. Pairwise gains use the reference and
the attempt alone.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCE = "reference"
SEEDS = ["reference", "reference_seed2", "reference_seed3"]


def load():
    ref = json.loads((ROOT / "scoring/reference.json").read_text())["experiments"]
    test = json.loads((HERE / "scores_test_all.json").read_text())
    train = json.loads((HERE / "scores_train_all.json").read_text())
    return ref, test, train


def gains(ref, scores, cohort):
    out = {c: 0.0 for c in cohort}
    for exp, spec in ref.items():
        results = scores["experiments"][exp]["results"]
        for metric, mdef in spec["metrics"].items():
            vals = np.array([results[c][metric] for c in cohort], dtype=float)
            std = float(np.std(vals))
            if std == 0.0:
                continue
            sign = 1.0 if mdef["higher_is_better"] else -1.0
            base = results[REFERENCE][metric]
            for c in cohort:
                out[c] += spec["weight"] * abs(mdef["coefficient"]) * sign * (results[c][metric] - base) / std
    return out


def main() -> None:
    ref, test, train = load()
    cases = sorted(test["experiments"][next(iter(ref))]["results"])
    shortcut = [c for c in cases if c.startswith("shortcut_") or c.startswith("zz_")]
    honest = [c for c in cases if c not in shortcut]
    main_gain = gains(ref, test, cases)
    honest_gain = gains(ref, test, honest)
    pair = {c: gains(ref, test, sorted({REFERENCE, c}))[c] for c in cases}
    train_main = gains(ref, train, cases)
    seed_vals = [honest_gain[s] for s in SEEDS if s in honest_gain]
    seed_spread_honest = max(seed_vals) - min(seed_vals) if seed_vals else None
    seed_vals_main = [main_gain[s] for s in SEEDS if s in main_gain]
    seed_spread_main = max(seed_vals_main) - min(seed_vals_main) if seed_vals_main else None
    diag = test.get("_diagnostics", {}).get("methods", {})
    summary = {
        "cases": cases,
        "honest_cohort": honest,
        "gain_all_cohort": main_gain,
        "gain_honest_cohort": honest_gain,
        "gain_pairwise": pair,
        "gain_all_cohort_train_slice": train_main,
        "seed_spread_honest_cohort": seed_spread_honest,
        "seed_spread_all_cohort": seed_spread_main,
        "status": {c: diag.get(c, {}).get("status") for c in cases},
        "errors": {c: diag[c].get("error") or diag[c].get("upsampling_error") for c in cases if c in diag and (diag[c].get("error") or diag[c].get("upsampling_error"))},
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))

    exps = list(ref)
    lines = ["# Hardening suite summary", ""]
    lines.append(f"Seed spread of rank gain: honest cohort {seed_spread_honest:.4f}, all cohort {seed_spread_main:.4f}.")
    lines.append("")
    header = "| case | status | gain (all) | gain (honest) | pairwise | " + " | ".join(f"{e} {ref[e]['primary_metric']}" for e in exps) + " |"
    lines += [header, "|" + "---|" * (5 + len(exps))]
    for c in sorted(cases, key=lambda c: -main_gain[c]):
        prim = [test["experiments"][e]["results"][c][ref[e]["primary_metric"]] for e in exps]
        hg = f"{honest_gain[c]:+.4f}" if c in honest_gain else "-"
        lines.append(
            f"| {c} | {summary['status'][c]} | {main_gain[c]:+.4f} | {hg} | {pair[c]:+.3f} | " + " | ".join(f"{v:.4g}" for v in prim) + " |"
        )
    lines.append("")
    lines.append("All metrics, test slice:")
    lines.append("")
    for e in exps:
        metrics = list(ref[e]["metrics"])
        lines.append(f"**{e}**")
        lines.append("")
        lines.append("| case | " + " | ".join(metrics) + " | train " + ref[e]["primary_metric"] + " |")
        lines.append("|" + "---|" * (len(metrics) + 2))
        for c in sorted(honest, key=lambda c: test["experiments"][e]["results"][c][ref[e]["primary_metric"]]):
            row = test["experiments"][e]["results"][c]
            tr = train["experiments"][e]["results"][c][ref[e]["primary_metric"]]
            lines.append(f"| {c} | " + " | ".join(f"{row[m]:.4g}" for m in metrics) + f" | {tr:.4g} |")
        lines.append("")
    (HERE / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
