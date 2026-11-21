#!/usr/bin/env python3
"""Build the curated spectral library and its fixed train/test split.

This follows the dataset construction of the paper (Sec. 4.4) as closely as
the public sources allow:

* Reflectances: the 1,269 measured matt Munsell chips (the paper's source),
  plus 36 bounded-least-squares "optimal" reflectances targeting the sRGB
  primaries (s in [0.6, 0.98], Y = 0.30) and 144 smooth basis-function
  reflectances (24 hue directions x 6 saturation levels, s in [0.7, 0.98]).
  Total 1,449, split 1,013 / 436 with angular-ring stratification in CIELAB
  a*b* (180 angular bins, per-bin radial quantile rings).
* Illuminants: measured / standard lamp tables (CIE FL, HP, LED, A, D65,
  ID65) plus 300 synthetic lamp-like spectra (phosphor white LEDs,
  triband fluorescents, metal halides) standing in for the paper's LSPDD
  lamp database, which needs an account; simulated CIE daylight, 82 synthetic blackbody broadband spectra,
  vertically flipped broadband spectra, and 367 synthetic narrowband spectra,
  greedily filtered at cosine similarity 0.95, normalised to unit peak and
  split 70/30 with 36 angular bins.

All spectra are box-resampled to 47 equally spaced samples over 368-830 nm
and zeroed outside 400-700 nm.

Writes the public training library ``data/spectra_train.json`` and the
held-out library ``eval/test/test_assets.json`` (hidden test only). The
split and the synthetic spectra depend on a seed that lives only here.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data" / "downloads" / "raw"
TRAIN_OUT = ROOT / "data" / "spectra_train.json"
TEST_OUT = HERE / "test_assets.json"
SEED = 2602_18741_07

WL = np.linspace(368.0, 830.0, 47)
STEP = float(WL[1] - WL[0])
MASK = ((WL >= 400.0) & (WL <= 700.0)).astype(np.float64)
VIS = MASK > 0
FINE = np.arange(360.0, 841.0, 1.0)

XYZ_TO_SRGB = np.array(
    [[3.2404542, -1.5371385, -0.4985314], [-0.9692660, 1.8760108, 0.0415560], [0.0556434, -0.2040259, 1.0572252]]
)
SRGB_TO_XYZ = np.linalg.inv(XYZ_TO_SRGB)


# ----------------------------------------------------------------------------
# Resampling helpers


def _bin_matrix() -> np.ndarray:
    a = np.zeros((WL.size, FINE.size))
    for i, c in enumerate(WL):
        sel = (FINE >= c - STEP / 2.0) & (FINE < c + STEP / 2.0)
        a[i, sel] = 1.0 / sel.sum()
    return a


BIN = _bin_matrix()


def resample(wl_src: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Box-average spectra (N, len(wl_src)) onto the 47-sample grid, masked."""
    values = np.atleast_2d(np.asarray(values, dtype=np.float64))
    fine = np.stack([np.interp(FINE, wl_src, v, left=0.0, right=0.0) for v in values])
    return (fine @ BIN.T) * MASK


def unit_peak(spectra: np.ndarray) -> np.ndarray:
    spectra = np.clip(np.asarray(spectra, dtype=np.float64), 0.0, None) * MASK
    peak = spectra.max(axis=1, keepdims=True)
    keep = peak[:, 0] > 1e-12
    out = spectra[keep] / peak[keep]
    return out


def read_csv(name: str) -> np.ndarray:
    rows = []
    for line in (RAW / name).read_text().strip().splitlines():
        line = line.strip()
        if line:
            rows.append([float(x) for x in line.split(",")])
    return np.asarray(rows, dtype=np.float64)


# ----------------------------------------------------------------------------
# Colorimetry (builder-local)


def load_cmf() -> np.ndarray:
    raw = read_csv("CIE_xyz_1931_2deg.csv")
    return resample(raw[:, 0], raw[:, 1:].T)  # (3, 47), masked, unnormalised


def load_d65() -> np.ndarray:
    raw = read_csv("CIE_std_illum_D65.csv")
    return unit_peak(resample(raw[:, 0], raw[:, 1]))[0]


def xyz_e(spectra: np.ndarray, cmf: np.ndarray) -> np.ndarray:
    """XYZ normalised so the equal-energy visible white has Y = 1."""
    return np.atleast_2d(spectra) @ cmf.T / float(cmf[1] @ MASK)


def lab_from_xyz(xyz: np.ndarray, white: np.ndarray) -> np.ndarray:
    t = np.clip(xyz / white, 0.0, None)
    d = 6.0 / 29.0
    f = np.where(t > d**3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], axis=1)


# ----------------------------------------------------------------------------
# Reflectances


def load_munsell() -> np.ndarray:
    with gzip.open(RAW / "munsell380_800_1.asc.gz", "rt") as fh:
        values = np.array(fh.read().split(), dtype=np.float64)
    if values.size != 421 * 1269:
        raise RuntimeError(f"unexpected Munsell value count {values.size}")
    spectra = values.reshape(1269, 421)
    return np.clip(resample(np.arange(380.0, 801.0, 1.0), spectra), 0.0, 1.0)


def _d65_weights(cmf: np.ndarray, d65: np.ndarray) -> np.ndarray:
    w = cmf * d65[None, :]
    return w / float(w[1] @ MASK)


def optimal_reflectances(cmf: np.ndarray, d65: np.ndarray) -> np.ndarray:
    """36 bounded least-squares reflectances toward the sRGB primaries (Eq. 9)."""
    w = _d65_weights(cmf, d65)[:, VIS]
    mu = 30.0
    out = []
    for primary in range(3):
        for s in np.linspace(0.6, 0.98, 12):
            rgb = (1.0 - s) * np.ones(3)
            rgb[primary] += s
            xyz_t = SRGB_TO_XYZ @ rgb
            xyz_t = xyz_t * (0.30 / xyz_t[1])
            a = np.stack([w[0], np.sqrt(mu) * w[1], w[2]])
            b = np.array([xyz_t[0], np.sqrt(mu) * xyz_t[1], xyz_t[2]])
            lip = 2.0 * np.linalg.norm(a, 2) ** 2
            r = np.full(a.shape[1], 0.5)
            y = r.copy()
            t = 1.0
            for _ in range(6000):  # FISTA with box projection
                grad = 2.0 * a.T @ (a @ y - b)
                r_next = np.clip(y - grad / lip, 0.0, 1.0)
                t_next = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * t * t))
                y = r_next + ((t - 1.0) / t_next) * (r_next - r)
                r, t = r_next, t_next
            full = np.zeros(WL.size)
            full[VIS] = r
            out.append(full)
    return np.asarray(out)


def _hsv_to_rgb(h: float, s: float, v: float) -> np.ndarray:
    i = int(np.floor(h * 6.0)) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    return np.array([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i])


def smooth_reflectances(cmf: np.ndarray, d65: np.ndarray) -> np.ndarray:
    """144 smooth reflectances from a sigmoid Gaussian basis (24 hues x 6 saturations)."""
    w = _d65_weights(cmf, d65)
    centers = np.linspace(400.0, 700.0, 10)
    basis = np.exp(-0.5 * ((WL[:, None] - centers[None, :]) / 25.0) ** 2) * MASK[:, None]
    out = []
    for hue in range(24):
        for s in np.linspace(0.7, 0.98, 6):
            target = SRGB_TO_XYZ @ _hsv_to_rgb(hue / 24.0, s, 0.8)
            c = np.zeros(basis.shape[1])
            m = np.zeros_like(c)
            v = np.zeros_like(c)
            for it in range(1, 4001):  # Adam on the basis coefficients
                sig = 1.0 / (1.0 + np.exp(-(basis @ c)))
                r = sig * MASK
                resid = w @ r - target
                grad = basis.T @ ((w.T @ (2.0 * resid)) * sig * (1.0 - sig) * MASK)
                m = 0.9 * m + 0.1 * grad
                v = 0.999 * v + 0.001 * grad * grad
                c -= 0.05 * (m / (1 - 0.9**it)) / (np.sqrt(v / (1 - 0.999**it)) + 1e-8)
            out.append((1.0 / (1.0 + np.exp(-(basis @ c)))) * MASK)
    return np.asarray(out)


# ----------------------------------------------------------------------------
# Illuminants


def daylight(cct: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    comp = read_csv("CIE_illum_Dxx_comp.csv")
    out = []
    for t in cct:
        if t <= 7000:
            xd = -4.6070e9 / t**3 + 2.9678e6 / t**2 + 0.09911e3 / t + 0.244063
        else:
            xd = -2.0064e9 / t**3 + 1.9018e6 / t**2 + 0.24748e3 / t + 0.237040
        yd = -3.000 * xd * xd + 2.870 * xd - 0.275
        m = 0.0241 + 0.2562 * xd - 0.7341 * yd
        m1 = (-1.3515 - 1.7703 * xd + 5.9114 * yd) / m
        m2 = (0.0300 - 31.4424 * xd + 30.0717 * yd) / m
        out.append(comp[:, 1] + m1 * comp[:, 2] + m2 * comp[:, 3])
    return comp[:, 0], np.asarray(out)


def blackbody(cct: np.ndarray) -> np.ndarray:
    lam = FINE * 1e-9
    c2 = 1.4387769e-2
    spectra = np.stack([lam**-5 / np.expm1(c2 / (lam * t)) for t in cct])
    return resample(FINE, spectra)


def narrowband(rng: np.random.Generator, count: int) -> np.ndarray:
    out = []
    for _ in range(count):
        n_peaks = int(rng.choice([1, 2, 3], p=[0.45, 0.35, 0.20]))
        spec = np.zeros_like(FINE)
        for j in range(n_peaks):
            center = rng.uniform(405.0, 695.0)
            fwhm = rng.uniform(5.0, 30.0)
            amp = 1.0 if j == 0 else rng.uniform(0.3, 1.0)
            spec += amp * np.exp(-0.5 * ((FINE - center) / (fwhm / 2.3548)) ** 2)
        if rng.random() < 0.5:
            spec += rng.uniform(0.0, 0.02) * ((FINE >= 400) & (FINE <= 700))
        out.append(spec)
    return resample(FINE, np.asarray(out))


def _gauss(center: float, fwhm: float) -> np.ndarray:
    return np.exp(-0.5 * ((FINE - center) / (fwhm / 2.3548)) ** 2)


def synthetic_lamps(rng: np.random.Generator) -> tuple[np.ndarray, list[str]]:
    """Lamp-like broadband spectra standing in for the LSPDD categories.

    Phosphor-converted white LEDs (blue pump + one or two broad phosphor bands),
    triband / halophosphate fluorescent lamps (mercury and rare-earth lines over
    a weak continuum) and metal-halide lamps (many lines over a continuum).
    """
    spectra, names = [], []
    for _ in range(200):
        spec = _gauss(rng.uniform(440.0, 465.0), rng.uniform(16.0, 26.0))
        if rng.random() < 0.6:
            spec = spec + rng.uniform(0.4, 2.5) * _gauss(rng.uniform(545.0, 600.0), rng.uniform(100.0, 150.0))
        else:
            spec = spec + rng.uniform(0.3, 1.5) * _gauss(rng.uniform(520.0, 550.0), rng.uniform(60.0, 100.0))
            spec = spec + rng.uniform(0.3, 1.5) * _gauss(rng.uniform(600.0, 650.0), rng.uniform(60.0, 100.0))
        spectra.append(spec)
        names.append("synthetic_led")
    for _ in range(60):
        spec = rng.uniform(0.02, 0.2) * _gauss(rng.uniform(500.0, 600.0), rng.uniform(150.0, 250.0))
        spec = spec + rng.uniform(0.0, 0.5) * _gauss(rng.uniform(440.0, 480.0), rng.uniform(30.0, 60.0))
        for line in (405.0, 436.0, 487.0, 546.0, 578.0, 611.0):
            spec = spec + rng.uniform(0.05, 1.0) * _gauss(line + rng.uniform(-2.0, 2.0), rng.uniform(3.0, 10.0))
        spectra.append(spec)
        names.append("synthetic_fluorescent")
    for _ in range(40):
        spec = rng.uniform(0.3, 1.0) * _gauss(rng.uniform(500.0, 600.0), rng.uniform(100.0, 200.0))
        for _ in range(int(rng.integers(10, 21))):
            spec = spec + rng.uniform(0.05, 0.6) * _gauss(rng.uniform(400.0, 700.0), rng.uniform(2.0, 6.0))
        spectra.append(spec)
        names.append("synthetic_metal_halide")
    return resample(FINE, np.asarray(spectra)), names


def flip(spectra: np.ndarray) -> np.ndarray:
    s = unit_peak(spectra)
    return unit_peak((1.0 - s) * MASK)


def greedy_cosine_filter(spectra: np.ndarray, tau: float = 0.95) -> np.ndarray:
    unit = spectra / np.linalg.norm(spectra, axis=1, keepdims=True)
    kept: list[int] = []
    for i in range(len(unit)):
        if not kept or float(np.max(unit[kept] @ unit[i])) < tau:
            kept.append(i)
    return np.asarray(kept, dtype=int)


def build_illuminants(rng: np.random.Generator) -> tuple[np.ndarray, list[str], list[str]]:
    groups: list[tuple[str, str, np.ndarray]] = []
    lamps = []
    lamp_names = []
    for name, prefix, labels in [
        ("CIE_illum_FLs.csv", "FL", [f"FL{i}" for i in range(1, 13)] + [f"FL3.{i}" for i in range(1, 16)]),
        ("CIE_illum_HPs.csv", "HP", [f"HP{i}" for i in range(1, 6)]),
        ("CIE_illum_LEDs.csv", "LED", ["LED-B1", "LED-B2", "LED-B3", "LED-B4", "LED-B5", "LED-BH1", "LED-RGB1", "LED-V1", "LED-V2"]),
    ]:
        raw = read_csv(name)
        if raw.shape[1] - 1 != len(labels):
            raise RuntimeError(f"{name}: expected {len(labels)} columns, got {raw.shape[1] - 1}")
        lamps.append(resample(raw[:, 0], raw[:, 1:].T))
        lamp_names += labels
    for name, label in [("CIE_std_illum_A_1nm.csv", "A"), ("CIE_std_illum_D65.csv", "D65"), ("CIE_illum_ID65.csv", "ID65")]:
        raw = read_csv(name)
        lamps.append(resample(raw[:, 0], raw[:, 1]))
        lamp_names.append(label)
    lamps_arr = np.concatenate(lamps)
    synth, synth_names = synthetic_lamps(rng)
    groups.append(("broadband", "lamp", lamps_arr))
    for source in ("synthetic_led", "synthetic_fluorescent", "synthetic_metal_halide"):
        groups.append(("broadband", source, synth[[i for i, n in enumerate(synth_names) if n == source]]))
    groups.append(("broadband", "lamp_flipped", flip(np.concatenate([lamps_arr, synth]))))
    bb = blackbody(np.geomspace(1500.0, 20000.0, 82))
    groups.append(("broadband", "blackbody", bb))
    groups.append(("broadband", "blackbody_flipped", flip(bb)))
    wl_d, day = daylight(np.geomspace(4000.0, 25000.0, 40))
    groups.append(("broadband", "daylight", resample(wl_d, day)))
    groups.append(("narrowband", "narrowband", narrowband(rng, 367)))

    spectra, types, sources = [], [], []
    for kind, source, arr in groups:
        arr = unit_peak(arr)
        spectra.append(arr)
        types += [kind] * len(arr)
        sources += [source] * len(arr)
    spectra_arr = np.concatenate(spectra)
    keep = greedy_cosine_filter(spectra_arr, 0.95)
    return spectra_arr[keep], [types[i] for i in keep], [sources[i] for i in keep]


# ----------------------------------------------------------------------------
# Splits


def largest_remainder(cell_ids: np.ndarray, n_test: int, rng: np.random.Generator) -> np.ndarray:
    cells, counts = np.unique(cell_ids, return_counts=True)
    quota = counts * (n_test / len(cell_ids))
    base = np.floor(quota).astype(int)
    extra = n_test - int(base.sum())
    frac = quota - base + 1e-9 * rng.random(len(cells))
    base[np.argsort(-frac)[:extra]] += 1
    is_test = np.zeros(len(cell_ids), dtype=bool)
    for cell, n in zip(cells, base):
        members = np.flatnonzero(cell_ids == cell)
        rng.shuffle(members)
        is_test[members[:n]] = True
    return is_test


def split_reflectances(refl: np.ndarray, cmf: np.ndarray, d65: np.ndarray, rng: np.random.Generator, n_test: int) -> np.ndarray:
    w = _d65_weights(cmf, d65)
    xyz = refl @ w.T
    white = w @ MASK
    lab = lab_from_xyz(xyz, white)
    center = np.median(lab[:, 1:], axis=0)
    rel = lab[:, 1:] - center
    angle = np.mod(np.arctan2(rel[:, 1], rel[:, 0]), 2 * np.pi)
    radius = np.hypot(rel[:, 0], rel[:, 1])
    ang_bin = np.minimum((angle / (2 * np.pi) * 180).astype(int), 179)
    ring = np.zeros(len(refl), dtype=int)
    for b in np.unique(ang_bin):
        idx = np.flatnonzero(ang_bin == b)
        if len(idx) >= 3:
            edges = np.quantile(radius[idx], [1 / 3, 2 / 3])
            ring[idx] = np.searchsorted(edges, radius[idx], side="right")
    return largest_remainder(ang_bin * 3 + ring, n_test, rng)


def split_illuminants(illum: np.ndarray, types: list[str], cmf: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    xyz = xyz_e(illum, cmf)
    xyz = xyz * (0.5 / np.maximum(xyz[:, 1:2], 1e-12))
    white = xyz_e(MASK[None, :], cmf)[0]
    lab = lab_from_xyz(xyz, white)
    angle = np.mod(np.arctan2(lab[:, 2], lab[:, 1]), 2 * np.pi)
    ang_bin = np.minimum((angle / (2 * np.pi) * 36).astype(int), 35)
    is_test = np.zeros(len(illum), dtype=bool)
    types_arr = np.asarray(types)
    for kind in ("broadband", "narrowband"):
        idx = np.flatnonzero(types_arr == kind)
        n_test = int(round(0.3 * len(idx)))
        sub = largest_remainder(ang_bin[idx], n_test, rng)
        is_test[idx[sub]] = True
    return is_test


# ----------------------------------------------------------------------------


def _round(a: np.ndarray) -> list:
    return np.vectorize(lambda x: float(f"{x:.7g}"))(np.asarray(a, dtype=np.float64)).tolist()


def _library(description, cmf, d65, refl, refl_src, illum, illum_type, illum_src) -> dict:
    return {
        "description": description,
        "wavelengths_nm": _round(WL),
        "visible_mask": _round(MASK),
        "cmf_xyz": _round(cmf),
        "d65": _round(d65),
        "reflectances": _round(refl),
        "reflectance_source": list(refl_src),
        "illuminants": _round(illum),
        "illuminant_type": list(illum_type),
        "illuminant_source": list(illum_src),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-out", default=str(TRAIN_OUT))
    parser.add_argument("--test-out", default=str(TEST_OUT))
    args = parser.parse_args()
    rng = np.random.default_rng(SEED)

    cmf = load_cmf()
    d65 = load_d65()
    munsell = load_munsell()
    optimal = optimal_reflectances(cmf, d65)
    smooth = smooth_reflectances(cmf, d65)
    refl = np.concatenate([munsell, optimal, smooth])
    refl_src = ["munsell"] * len(munsell) + ["optimal_srgb"] * len(optimal) + ["smooth_basis"] * len(smooth)
    refl_test = split_reflectances(refl, cmf, d65, rng, n_test=436)

    illum, illum_type, illum_src = build_illuminants(rng)
    illum_test = split_illuminants(illum, illum_type, cmf, rng)

    def pick(arr, sel):
        return [arr[i] for i in np.flatnonzero(sel)]

    train = _library(
        "Public training spectra (47 samples, 368-830 nm, zero outside 400-700 nm).",
        cmf, d65,
        refl[~refl_test], pick(refl_src, ~refl_test),
        illum[~illum_test], pick(illum_type, ~illum_test), pick(illum_src, ~illum_test),
    )
    test = _library(
        "Held-out test spectra for the hidden evaluator only.",
        cmf, d65,
        refl[refl_test], pick(refl_src, refl_test),
        illum[illum_test], pick(illum_type, illum_test), pick(illum_src, illum_test),
    )
    Path(args.train_out).write_text(json.dumps(train, separators=(",", ":")))
    Path(args.test_out).write_text(json.dumps(test, separators=(",", ":")))
    report = {
        "reflectances": {"total": len(refl), "train": int((~refl_test).sum()), "test": int(refl_test.sum())},
        "illuminants": {
            "total": len(illum),
            "train": {k: int(sum(1 for t, s in zip(illum_type, illum_test) if t == k and not s)) for k in ("broadband", "narrowband")},
            "test": {k: int(sum(1 for t, s in zip(illum_type, illum_test) if t == k and s)) for k in ("broadband", "narrowband")},
            "sources_kept": {s: illum_src.count(s) for s in sorted(set(illum_src))},
        },
        "munsell_max_reflectance": float(munsell.max()),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
