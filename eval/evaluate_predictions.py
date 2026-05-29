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

from data.spectral_common import make_multibounce_chains, make_product_pairs, summarize_color_error, summarize_xyz_error  # noqa: E402


def fixed_target(exp_name: str, count: int) -> np.ndarray:
    """Regenerate held-out targets independently of candidate output files."""
    if exp_name == "spectral_product_broadband":
        reflectance, illumination = make_product_pairs("broadband", count=count)
        return reflectance * illumination
    if exp_name in {"spectral_product_narrowband", "rgb_upsampling_narrowband"}:
        reflectance, illumination = make_product_pairs("narrowband", count=count)
        return reflectance * illumination
    if exp_name == "multibounce_narrowband":
        reflectances, illumination = make_multibounce_chains("narrowband", count=count, bounces=3)
        target = illumination.copy()
        for bounce in range(reflectances.shape[1]):
            target = target * reflectances[:, bounce, :]
        return target
    raise ValueError(f"No fixed evaluation target registered for experiment {exp_name!r}")


def score_run(path: Path) -> tuple[str, dict]:
    payload = json.loads((path / "predictions.json").read_text())
    method = payload["method"]
    result: dict[str, dict[str, float]] = {}
    for exp_name, exp in payload["experiments"].items():
        if "pred_spectrum" in exp:
            pred = np.asarray(exp["pred_spectrum"], dtype=np.float32)
            target = fixed_target(exp_name, len(pred))
            metrics = summarize_color_error(pred, target)
        elif "pred_xyz" in exp:
            pred_xyz = np.asarray(exp["pred_xyz"], dtype=np.float32)
            target = fixed_target(exp_name, len(pred_xyz))
            metrics = summarize_xyz_error(pred_xyz, target)
        else:
            raise ValueError(f"{path} lacks pred_spectrum or pred_xyz for {exp_name}")
        metrics["render_passes"] = float(payload.get("render_passes", math.nan))
        metrics["latent_channels"] = float(payload.get("k", math.nan))
        metrics["output_wavelengths"] = float(payload.get("output_wavelengths", payload.get("spectral_samples", math.nan)))
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
