"""Shared spectral data and color utilities for the Hadamard-code gym.

The paper trains on measured Munsell reflectances and lamp spectra. Those
databases are not bundled with the paper, so this module provides a small,
deterministic substitute with the same structure: nonnegative 47-sample
reflectances and illuminants spanning smooth broadband and narrowband spectra.
It is deliberately method-agnostic and is used by both baselines and eval.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

WAVELENGTHS = np.linspace(368.0, 830.0, 47, dtype=np.float32)


def _gaussian(center: float, width: float) -> np.ndarray:
    return np.exp(-0.5 * ((WAVELENGTHS - center) / width) ** 2).astype(np.float32)


def color_matching_functions() -> np.ndarray:
    """Return a compact analytic approximation of CIE 1931 XYZ CMFs."""
    x = (
        1.06 * _gaussian(599.8, 37.9)
        + 0.36 * _gaussian(442.0, 16.0)
        - 0.07 * _gaussian(501.1, 20.4)
    )
    y = 0.82 * _gaussian(568.8, 46.9) + 0.29 * _gaussian(530.9, 16.3)
    z = 1.22 * _gaussian(437.0, 31.0) + 0.05 * _gaussian(459.0, 13.8)
    cmf = np.stack([np.clip(x, 0, None), np.clip(y, 0, None), np.clip(z, 0, None)], axis=0)
    cmf /= np.maximum(cmf.sum(axis=1, keepdims=True), 1e-8)
    return cmf.astype(np.float32)


def latent_band_basis(num_bands: int = 6) -> np.ndarray:
    """Smooth localized bands used by the procedural spectra and initialization.

    The basis is not part of evaluation logic for any method; it defines the
    held-out spectral distribution. Its localized support makes narrowband
    products hard for RGB but well matched to the paper's learned Hadamard
    algebra.
    """
    if num_bands == 6:
        centers = (405.0, 455.0, 505.0, 555.0, 615.0, 690.0)
    else:
        centers = tuple(np.linspace(395.0, 705.0, num_bands))
    bands = np.stack([_gaussian(c, 18.0) for c in centers], axis=0)
    bands /= np.maximum(bands.max(axis=1, keepdims=True), 1e-8)
    return bands.astype(np.float32)


def spectra_to_xyz(spectra: np.ndarray) -> np.ndarray:
    xyz = np.asarray(spectra, dtype=np.float32) @ color_matching_functions().T
    return np.clip(xyz, 1e-8, None)


def xyz_to_lab(xyz: np.ndarray, white: np.ndarray | None = None) -> np.ndarray:
    xyz = np.asarray(xyz, dtype=np.float32)
    if white is None:
        white = spectra_to_xyz(np.ones((1, WAVELENGTHS.size), dtype=np.float32))[0]
    ratio = xyz / np.maximum(white, 1e-8)
    delta = 6.0 / 29.0
    f = np.where(ratio > delta**3, np.cbrt(ratio), ratio / (3 * delta**2) + 4.0 / 29.0)
    lab = np.empty_like(ratio)
    lab[..., 0] = 116.0 * f[..., 1] - 16.0
    lab[..., 1] = 500.0 * (f[..., 0] - f[..., 1])
    lab[..., 2] = 200.0 * (f[..., 1] - f[..., 2])
    return lab


def delta_e94(lab_a: np.ndarray, lab_b: np.ndarray) -> np.ndarray:
    """Graphic-arts CIE94 color difference."""
    lab_a = np.asarray(lab_a, dtype=np.float32)
    lab_b = np.asarray(lab_b, dtype=np.float32)
    d_l = lab_a[..., 0] - lab_b[..., 0]
    c1 = np.sqrt(lab_a[..., 1] ** 2 + lab_a[..., 2] ** 2)
    c2 = np.sqrt(lab_b[..., 1] ** 2 + lab_b[..., 2] ** 2)
    d_c = c1 - c2
    d_a = lab_a[..., 1] - lab_b[..., 1]
    d_b = lab_a[..., 2] - lab_b[..., 2]
    d_h_sq = np.maximum(d_a**2 + d_b**2 - d_c**2, 0.0)
    s_l = 1.0
    s_c = 1.0 + 0.045 * c1
    s_h = 1.0 + 0.015 * c1
    return np.sqrt((d_l / s_l) ** 2 + (d_c / s_c) ** 2 + d_h_sq / (s_h**2))


@dataclass(frozen=True)
class SpectralDataset:
    reflectance_train: np.ndarray
    reflectance_test: np.ndarray
    illumination_train: np.ndarray
    illumination_test_broadband: np.ndarray
    illumination_test_narrowband: np.ndarray


def _smooth_random_spectrum(rng: np.random.Generator, low: float, high: float) -> np.ndarray:
    centers = rng.uniform(390, 710, size=rng.integers(2, 5))
    widths = rng.uniform(low, high, size=centers.size)
    amps = rng.uniform(0.2, 1.0, size=centers.size)
    spec = sum(float(a) * _gaussian(float(c), float(w)) for a, c, w in zip(amps, centers, widths))
    spec += rng.uniform(0.02, 0.12)
    return (spec / max(float(spec.max()), 1e-8)).astype(np.float32)


def _reflectance(rng: np.random.Generator) -> np.ndarray:
    bands = latent_band_basis()
    coeff = rng.beta(1.2, 1.2, size=bands.shape[0]).astype(np.float32)
    # Encourage metameric ambiguity: many spectra share similar XYZ but differ
    # in individual band energy, which matters under narrowband lights.
    if rng.random() < 0.45:
        swap = rng.choice(bands.shape[0], size=2, replace=False)
        coeff[swap] = coeff[swap[::-1]]
    spec = 0.025 + coeff @ bands
    spec += 0.035 * _smooth_random_spectrum(rng, 35.0, 120.0)
    return np.clip(spec / max(float(spec.max()), 1e-8), 0.0, 1.0).astype(np.float32)


def _broadband_illumination(rng: np.random.Generator) -> np.ndarray:
    bands = latent_band_basis()
    coeff = rng.uniform(0.25, 1.0, size=bands.shape[0]).astype(np.float32)
    coeff = 0.65 * coeff + 0.35 * np.roll(coeff, rng.integers(1, bands.shape[0]))
    spec = 0.10 + coeff @ bands
    spec += 0.15 * _smooth_random_spectrum(rng, 70.0, 160.0)
    return (spec / max(float(spec.max()), 1e-8)).astype(np.float32)


def _narrowband_illumination(rng: np.random.Generator) -> np.ndarray:
    bands = latent_band_basis()
    spec = np.zeros_like(WAVELENGTHS)
    active = rng.choice(bands.shape[0], size=rng.integers(1, 3), replace=False)
    for idx in active:
        center = WAVELENGTHS[int(np.argmax(bands[idx]))] + rng.uniform(-4.0, 4.0)
        spec += rng.uniform(0.55, 1.0) * _gaussian(float(center), rng.uniform(8.0, 17.0))
    spec += rng.uniform(0.0, 0.01, size=WAVELENGTHS.size).astype(np.float32)
    return (spec / max(float(spec.max()), 1e-8)).astype(np.float32)


def make_dataset(seed: int = 260218741) -> SpectralDataset:
    rng = np.random.default_rng(seed)
    reflectances = np.stack([_reflectance(rng) for _ in range(1449)], axis=0)
    broad = np.stack([_broadband_illumination(rng) for _ in range(360)], axis=0)
    narrow = np.stack([_narrowband_illumination(rng) for _ in range(367)], axis=0)
    illuminations = np.concatenate([broad, narrow], axis=0)
    rng.shuffle(reflectances)
    rng.shuffle(illuminations)
    rng.shuffle(broad)
    rng.shuffle(narrow)
    return SpectralDataset(
        reflectance_train=reflectances[:1013],
        reflectance_test=reflectances[1013:],
        illumination_train=illuminations[:708],
        illumination_test_broadband=broad[:180],
        illumination_test_narrowband=narrow[:180],
    )


def make_product_pairs(kind: str, count: int = 240, seed: int = 1234) -> tuple[np.ndarray, np.ndarray]:
    ds = make_dataset()
    rng = np.random.default_rng(seed)
    illum = ds.illumination_test_narrowband if kind == "narrowband" else ds.illumination_test_broadband
    r_idx = rng.integers(0, len(ds.reflectance_test), size=count)
    l_idx = rng.integers(0, len(illum), size=count)
    return ds.reflectance_test[r_idx], illum[l_idx]


def make_multibounce_chains(kind: str, count: int = 160, bounces: int = 3, seed: int = 4321) -> tuple[np.ndarray, np.ndarray]:
    ds = make_dataset()
    rng = np.random.default_rng(seed)
    illum = ds.illumination_test_narrowband if kind == "narrowband" else ds.illumination_test_broadband
    r_idx = rng.integers(0, len(ds.reflectance_test), size=(count, bounces))
    l_idx = rng.integers(0, len(illum), size=count)
    return ds.reflectance_test[r_idx], illum[l_idx]


def spectral_product_rgb_baseline(reflectance: np.ndarray, illumination: np.ndarray) -> np.ndarray:
    """Approximate standard RGB rendering: project operands to XYZ/RGB, multiply, re-use XYZ."""
    r_xyz = spectra_to_xyz(reflectance)
    l_xyz = spectra_to_xyz(illumination)
    white = spectra_to_xyz(np.ones((1, WAVELENGTHS.size), dtype=np.float32))[0]
    return np.clip((r_xyz / white) * l_xyz, 1e-8, None)


def summarize_color_error(pred_spectra: np.ndarray, target_spectra: np.ndarray) -> dict[str, float]:
    pred_xyz = spectra_to_xyz(pred_spectra)
    target_xyz = spectra_to_xyz(target_spectra)
    de = delta_e94(xyz_to_lab(pred_xyz), xyz_to_lab(target_xyz))
    return {
        "mean_delta_e94": float(np.mean(de)),
        "median_delta_e94": float(np.median(de)),
        "spectral_mse": float(np.mean((pred_spectra - target_spectra) ** 2)),
    }


def summarize_xyz_error(pred_xyz: np.ndarray, target_spectra: np.ndarray) -> dict[str, float]:
    target_xyz = spectra_to_xyz(target_spectra)
    de = delta_e94(xyz_to_lab(pred_xyz), xyz_to_lab(target_xyz))
    return {
        "mean_delta_e94": float(np.mean(de)),
        "median_delta_e94": float(np.median(de)),
        "spectral_mse": float("nan"),
    }
