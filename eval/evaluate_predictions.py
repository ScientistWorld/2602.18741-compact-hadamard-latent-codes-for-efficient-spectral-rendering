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


def load_reference_contract(path: Path | None) -> dict[str, set[str]] | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text())
    return {
        exp_name: set(exp.get("results", {}).keys())
        for exp_name, exp in payload.get("experiments", {}).items()
        if isinstance(exp, dict)
    }


def merge_scores(runs: list[Path], reference_contract: dict[str, set[str]] | None = None) -> tuple[dict, dict]:
    merged: dict[str, dict] = {"experiments": {}}
    extra: dict[str, dict] = {"experiments": {}}
    for run in runs:
        _, scored = score_run(run)
        for exp, methods in scored.items():
            for method_name, metrics in methods.items():
                official = (
                    reference_contract is None
                    or (exp in reference_contract and method_name in reference_contract[exp])
                )
                target = merged if official else extra
                target["experiments"].setdefault(exp, {"results": {}})
                target["experiments"][exp]["results"][method_name] = metrics
    return merged, extra


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", default=["outputs/hadamard_k6", "outputs/rgb_baseline"])
    parser.add_argument("--output", default="scoring/scores.json")
    parser.add_argument(
        "--reference",
        default="scoring/reference.json",
        help="Reference contract used to filter official scores; missing path disables filtering.",
    )
    parser.add_argument(
        "--extra-output",
        default="scoring/extra_scores.json",
        help="Where to write experiments not present in the reference contract.",
    )
    parser.add_argument(
        "--include-extra",
        action="store_true",
        help="Write all experiments to --output instead of filtering to --reference.",
    )
    args = parser.parse_args()
    contract = None if args.include_extra else load_reference_contract(Path(args.reference))
    scores, extra_scores = merge_scores([Path(p) for p in args.runs], contract)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True))
    extra_out = Path(args.extra_output)
    if extra_scores["experiments"]:
        extra_out.parent.mkdir(parents=True, exist_ok=True)
        extra_out.write_text(json.dumps(extra_scores, indent=2, sort_keys=True))
    elif extra_out.exists():
        extra_out.unlink()
    print(json.dumps(scores, indent=2, sort_keys=True))
    if extra_scores["experiments"]:
        print(f"Wrote non-reference diagnostic scores to {extra_out}")


if __name__ == "__main__":
    main()
