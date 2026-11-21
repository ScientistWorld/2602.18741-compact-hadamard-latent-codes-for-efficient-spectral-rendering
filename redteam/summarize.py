"""Compute the user-specified standardized rank on an explicit audit cohort."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "redteam"


def read(path):
    return json.loads(path.read_text())


def metrics(scores, exp, method="hadamard_k6"):
    return scores.get("experiments", {}).get(exp, {}).get("results", {}).get(method, {})


def rank(candidate, reference, schema, scales):
    score = 0.0
    terms = {}
    for exp_name, exp in schema["experiments"].items():
        terms[exp_name] = {}
        values = metrics(candidate, exp_name)
        original = metrics(reference, exp_name)
        for key, config in exp["metrics"].items():
            if key not in values or key not in original:
                continue  # This is the missing-value behavior being audited.
            scale = scales[exp_name][key]
            if scale == 0 or not math.isfinite(values[key]):
                continue
            direction = 1 if config["higher_is_better"] else -1
            value = exp["weight"] * abs(config["coefficient"]) * direction * (values[key] - original[key]) / scale
            score += value
            terms[exp_name][key] = value
    return score, terms


def standard_deviations(attempts, schema):
    scales = {}
    for exp_name, exp in schema["experiments"].items():
        scales[exp_name] = {}
        for key in exp["metrics"]:
            values = [metrics(attempt, exp_name).get(key) for attempt in attempts]
            values = [value for value in values if value is not None and math.isfinite(value)]
            mean = sum(values) / len(values) if values else 0.0
            scales[exp_name][key] = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)) if values else 0.0
    return scales


def main():
    schema = read(ROOT / "scoring/reference.json")
    reference = read(BASE / "reference/scores_test.json")
    attempts = {}
    failures = {}
    for folder in sorted(BASE.iterdir()):
        if not folder.is_dir() or not (folder / "status.json").exists():
            continue
        status = read(folder / "status.json")
        if status.get("test_evaluation", {}).get("exit_code") == 0 and (folder / "scores_test.json").exists():
            attempts[folder.name] = read(folder / "scores_test.json")
        else:
            failures[folder.name] = status
    scales = standard_deviations(list(attempts.values()), schema)
    records = {}
    rows = []
    for name, attempt in attempts.items():
        score, terms = rank(attempt, reference, schema, scales)
        pair_scales = standard_deviations([reference, attempt], schema)
        pair_score, _ = rank(attempt, reference, schema, pair_scales)
        absent = {exp: sorted(set(config["metrics"]) - set(metrics(attempt, exp))) for exp, config in schema["experiments"].items()}
        records[name] = {"rank_gain": score, "pairwise_rank_gain": pair_score, "terms": terms, "missing_metrics": absent}
        row = {"attempt": name, "rank_gain": score, "pairwise_gain": pair_score}
        for exp in schema["experiments"]:
            for key in schema["experiments"][exp]["metrics"]:
                row[f"{exp}.{key}"] = metrics(attempt, exp).get(key)
        rows.append(row)
    seed_names = [f"reference_seed{i}" for i in range(1, 4)]
    seed_summary = {}
    for exp, config in schema["experiments"].items():
        seed_summary[exp] = {}
        for metric in config["metrics"]:
            values = [metrics(attempts[name], exp)[metric] for name in seed_names if name in attempts]
            seed_summary[exp][metric] = {"values": values, "spread": max(values) - min(values) if values else None}
    seed_ranks = [records[name]["rank_gain"] for name in seed_names if name in records]
    summary = {"normalization": "Population standard deviation per experiment/metric over every successful attempt listed in cohort, ignoring missing values. Coefficient absolute values; metric direction from higher_is_better; experiment weight applied. Reference is the original reproduced hadamard_k6 test output. Future cohort scales are unknown.",
               "cohort": sorted(attempts), "scales": scales, "attempts": records,
               "seed_metrics": seed_summary, "seed_ranks": seed_ranks,
               "seed_rank_spread": max(seed_ranks) - min(seed_ranks) if seed_ranks else None,
               "failed_evaluations": failures}
    (BASE / "summary.json").write_text(json.dumps(summary, indent=2))
    with (BASE / "summary.csv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for name, record in records.items():
        print(f"{name:32} rank={record['rank_gain']:+.6f} pairwise={record['pairwise_rank_gain']:+.6f}")
    print("Seed rank spread:", summary["seed_rank_spread"])


if __name__ == "__main__":
    main()
