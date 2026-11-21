#!/usr/bin/env python3
"""Standard RGB rendering expressed as a 3-channel codec (one RGB pass).

Assets are converted to linear sRGB the way an RGB pipeline stores them:
reflectances as albedo (sRGB under D65 divided by sRGB of D65, so white maps
to 1, 1, 1) and lights as linear-sRGB radiance. Rendering multiplies these
per channel (negative out-of-gamut values are clamped by the renderer). The
rendered RGB is turned back into a spectrum with three fixed nonnegative,
smooth primaries whose XYZ equals the sRGB primaries, so the decoded colour is
exactly the RGB render's colour. Legacy RGB assets need no upsampling: the
upsampler is the identity.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.spectral_data import (  # noqa: E402
    LINEAR_SRGB_TO_XYZ,
    illuminant_rgb_matrix,
    load_library,
    reflectance_rgb_matrix,
    xyz_matrix,
)


def nonnegative_primaries(lib, iterations: int = 200_000, smooth: float = 1e-6) -> np.ndarray:
    """(47, 3) nonnegative smooth spectra B with XYZ(B) = sRGB primaries (projected gradient)."""
    vis = lib.visible_mask > 0
    x = xyz_matrix(lib)[:, vis]
    n = x.shape[1]
    d2 = np.diff(np.eye(n), n=2, axis=0)
    target = LINEAR_SRGB_TO_XYZ
    lip = 2.0 * np.linalg.norm(x, 2) ** 2 + 2.0 * smooth * np.linalg.norm(d2, 2) ** 2
    b = np.full((n, 3), 0.5)
    y = b.copy()
    t = 1.0
    for _ in range(iterations):
        grad = 2.0 * x.T @ (x @ y - target) + 2.0 * smooth * d2.T @ (d2 @ y)
        b_next = np.clip(y - grad / lip, 0.0, None)
        t_next = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * t * t))
        y = b_next + ((t - 1.0) / t_next) * (b_next - b)
        b, t = b_next, t_next
    full = np.zeros((lib.visible_mask.size, 3))
    full[vis] = b
    return full


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default="outputs/rgb_baseline")
    args = parser.parse_args()
    lib = load_library()
    primaries = nonnegative_primaries(lib)
    residual = float(np.abs(xyz_matrix(lib) @ primaries - LINEAR_SRGB_TO_XYZ).max())
    codec = {
        "method": "rgb_baseline",
        "k": 3,
        "encoder_reflectance": reflectance_rgb_matrix(lib).tolist(),
        "encoder_illuminant": illuminant_rgb_matrix(lib).tolist(),
        "decoder": primaries.tolist(),
        "upsampler": np.eye(3).tolist(),
    }
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "codec.json").write_text(json.dumps(codec))
    print(json.dumps({"primaries_xyz_max_abs_residual": residual}))


if __name__ == "__main__":
    main()
