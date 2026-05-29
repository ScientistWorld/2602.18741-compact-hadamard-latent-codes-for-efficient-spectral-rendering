#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from data.spectral_common import (  # noqa: E402
    make_multibounce_chains,
    make_product_pairs,
    summarize_color_error,
    summarize_xyz_error,
)

SLICE = "test"


def discover_runs(outputs_dir: Path = Path("outputs")) -> list[Path]:
    if not outputs_dir.exists():
        return []
    return sorted(path.parent for path in outputs_dir.glob("*/predictions.json"))


def reference_experiments(path: Path | None) -> set[str] | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text())
    return set(payload.get("experiments", {}).keys())


def required_methods_from_train(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    payload = json.loads(path.read_text())
    required: set[str] = set()
    for exp in payload.get("experiments", {}).values():
        required.update(exp.get("results", {}).keys())
    return required


def select_runs_for_methods(candidates: list[Path], required_methods: set[str]) -> list[Path]:
    if not required_methods:
        return candidates
    by_method: dict[str, Path] = {}
    for path in candidates:
        predictions = path / "predictions.json"
        if not predictions.exists():
            continue
        method = json.loads(predictions.read_text()).get("method")
        if method in required_methods and method not in by_method:
            by_method[method] = path
    missing = sorted(required_methods.difference(by_method))
    if missing:
        raise SystemExit(
            "Cannot locate prediction outputs for train-scored methods: "
            + ", ".join(missing)
            + ". Expected outputs/*/predictions.json or explicit run paths."
        )
    return [by_method[name] for name in sorted(required_methods)]


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


def slice_bounds(count: int) -> tuple[int, int]:
    if count < 2:
        raise ValueError(f"{SLICE} split requires at least two predictions, got {count}")
    return count // 2, count


def score_run(path: Path, allowed_experiments: set[str] | None) -> tuple[str, dict]:
    payload = json.loads((path / "predictions.json").read_text())
    method = payload["method"]
    result: dict[str, dict[str, dict[str, float]]] = {}
    for exp_name, exp in payload["experiments"].items():
        if allowed_experiments is not None and exp_name not in allowed_experiments:
            continue
        if "pred_spectrum" in exp:
            pred_full = np.asarray(exp["pred_spectrum"], dtype=np.float32)
            start, end = slice_bounds(len(pred_full))
            pred = pred_full[start:end]
            target = fixed_target(exp_name, len(pred_full))[start:end]
            metrics = summarize_color_error(pred, target)
        elif "pred_xyz" in exp:
            pred_full = np.asarray(exp["pred_xyz"], dtype=np.float32)
            start, end = slice_bounds(len(pred_full))
            pred_xyz = pred_full[start:end]
            target = fixed_target(exp_name, len(pred_full))[start:end]
            metrics = summarize_xyz_error(pred_xyz, target)
        else:
            raise ValueError(f"{path} lacks pred_spectrum or pred_xyz for {exp_name}")
        metrics["render_passes"] = float(payload.get("render_passes", math.nan))
        metrics["latent_channels"] = float(payload.get("k", math.nan))
        metrics["output_wavelengths"] = float(
            payload.get("output_wavelengths", payload.get("spectral_samples", math.nan))
        )
        metrics = {k: v for k, v in metrics.items() if not (isinstance(v, float) and math.isnan(v))}
        result[exp_name] = {method: metrics}
    return method, result


def merge_scores(runs: list[Path], allowed_experiments: set[str] | None) -> dict:
    merged: dict[str, dict] = {"experiments": {}}
    for run in runs:
        _, scored = score_run(run, allowed_experiments)
        for exp, methods in scored.items():
            for method_name, metrics in methods.items():
                merged["experiments"].setdefault(exp, {"results": {}})
                merged["experiments"][exp]["results"][method_name] = metrics
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", help="Output directories containing predictions.json files.")
    parser.add_argument("--output", default="scoring/scores_test.json")
    parser.add_argument(
        "--reference",
        default="scoring/reference.json",
        help="Reference schema used only to select official experiment names.",
    )
    parser.add_argument(
        "--match-train",
        default="scoring/scores_train.json",
        help="When present, score exactly the methods found in this train-slice score file.",
    )
    args = parser.parse_args()

    explicit_runs = [Path(p) for p in args.runs]
    candidates = explicit_runs + [p for p in discover_runs() if p not in explicit_runs]
    required_methods = required_methods_from_train(Path(args.match_train))
    runs = select_runs_for_methods(candidates, required_methods)
    if not runs:
        raise SystemExit("No prediction runs found. Pass output directories or create outputs/*/predictions.json.")
    allowed = reference_experiments(Path(args.reference))
    scores = merge_scores(runs, allowed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True))
    print(json.dumps(scores, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
