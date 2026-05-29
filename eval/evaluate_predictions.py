#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from data.spectral_common import summarize_color_error, summarize_xyz_error  # noqa: E402


def score_run(path: Path) -> tuple[str, dict]:
    payload = json.loads((path / "predictions.json").read_text())
    method = payload["method"]
    result: dict[str, dict[str, float]] = {}
    for exp_name, exp in payload["experiments"].items():
        target = np.asarray(exp["target_spectrum"], dtype=np.float32)
        if "pred_spectrum" in exp:
            pred = np.asarray(exp["pred_spectrum"], dtype=np.float32)
            metrics = summarize_color_error(pred, target)
        elif "pred_xyz" in exp:
            pred_xyz = np.asarray(exp["pred_xyz"], dtype=np.float32)
            metrics = summarize_xyz_error(pred_xyz, target)
        else:
            raise ValueError(f"{path} lacks pred_spectrum or pred_xyz for {exp_name}")
        metrics["render_passes"] = float(payload.get("render_passes", math.nan))
        metrics["spectral_samples"] = float(payload.get("spectral_samples", math.nan))
        metrics = {k: v for k, v in metrics.items() if not (isinstance(v, float) and math.isnan(v))}
        result[exp_name] = {method: metrics}
    return method, result


def merge_scores(runs: list[Path]) -> dict:
    merged: dict[str, dict] = {"experiments": {}}
    for run in runs:
        _, scored = score_run(run)
        for exp, methods in scored.items():
            merged["experiments"].setdefault(exp, {"results": {}})
            merged["experiments"][exp]["results"].update(methods)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", default=["outputs/hadamard_k6", "outputs/rgb_baseline"])
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()
    scores = merge_scores([Path(p) for p in args.runs])
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True))
    print(json.dumps(scores, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
