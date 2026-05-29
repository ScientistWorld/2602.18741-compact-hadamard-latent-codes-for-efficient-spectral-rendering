#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from data.spectral_common import (  # noqa: E402
    WAVELENGTHS,
    make_multibounce_chains,
    make_product_pairs,
    spectral_product_rgb_baseline,
)


def product(kind: str, count: int) -> dict:
    r, l = make_product_pairs(kind, count=count)
    target = r * l
    pred_xyz = spectral_product_rgb_baseline(r, l)
    return {
        "reflectance": r.tolist(),
        "illumination": l.tolist(),
        "target_spectrum": target.tolist(),
        "pred_xyz": pred_xyz.tolist(),
    }


def multibounce(kind: str, count: int) -> dict:
    reflectances, illumination = make_multibounce_chains(kind, count=count, bounces=3)
    target = illumination.copy()
    pred_xyz = None
    for bounce in range(reflectances.shape[1]):
        target = target * reflectances[:, bounce, :]
        if pred_xyz is None:
            pred_xyz = spectral_product_rgb_baseline(reflectances[:, bounce, :], illumination)
        else:
            # Continue in tristimulus space, mimicking a renderer that has already
            # discarded spectral shape after the first interaction.
            r_xyz = spectral_product_rgb_baseline(reflectances[:, bounce, :], np.ones_like(illumination))
            pred_xyz = pred_xyz * r_xyz
    return {
        "reflectance_chain": reflectances.tolist(),
        "illumination": illumination.tolist(),
        "target_spectrum": target.tolist(),
        "pred_xyz": np.clip(pred_xyz, 1e-8, None).tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/rgb_baseline")
    parser.add_argument("--eval-count", type=int, default=240)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "method": "rgb_baseline",
        "k": 3,
        "render_passes": 1,
        "spectral_samples": int(WAVELENGTHS.size),
        "experiments": {
            "spectral_product_broadband": product("broadband", args.eval_count),
            "spectral_product_narrowband": product("narrowband", args.eval_count),
            "multibounce_narrowband": multibounce("narrowband", max(80, args.eval_count // 2)),
        },
    }
    (out / "predictions.json").write_text(json.dumps(payload))


if __name__ == "__main__":
    main()
