"""Public spectral data and colorimetry helpers for the compact spectral-rendering gym.

The training library ``data/spectra_train.json`` holds measured and curated
reflectance and illuminant spectra on the paper's 47-sample grid
(368-830 nm, zero outside 400-700 nm). Everything here is method-agnostic and
mirrors the colorimetric conventions documented in ``briefing/evaluation.md``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

TRAIN_FILE = Path(__file__).resolve().parent / "spectra_train.json"

# Linear sRGB (D65 white, Y_white = 1) <-> CIE XYZ.
XYZ_TO_LINEAR_SRGB = np.array(
    [[3.2404542, -1.5371385, -0.4985314], [-0.9692660, 1.8760108, 0.0415560], [0.0556434, -0.2040259, 1.0572252]]
)
LINEAR_SRGB_TO_XYZ = np.linalg.inv(XYZ_TO_LINEAR_SRGB)


@dataclass(frozen=True)
class SpectralLibrary:
    wavelengths: np.ndarray  # (47,)
    visible_mask: np.ndarray  # (47,)
    cmf: np.ndarray  # (3, 47) CIE 1931 2-degree, box-resampled, zero outside 400-700 nm
    d65: np.ndarray  # (47,) unit peak
    reflectances: np.ndarray  # (N_R, 47) in [0, 1]
    reflectance_source: list
    illuminants: np.ndarray  # (N_L, 47) unit peak
    illuminant_type: list  # "broadband" | "narrowband"
    illuminant_source: list

    @property
    def broadband(self) -> np.ndarray:
        return self.illuminants[np.asarray(self.illuminant_type) == "broadband"]

    @property
    def narrowband(self) -> np.ndarray:
        return self.illuminants[np.asarray(self.illuminant_type) == "narrowband"]


def load_library(path: str | Path = TRAIN_FILE) -> SpectralLibrary:
    payload = json.loads(Path(path).read_text())
    return SpectralLibrary(
        wavelengths=np.asarray(payload["wavelengths_nm"], dtype=np.float64),
        visible_mask=np.asarray(payload["visible_mask"], dtype=np.float64),
        cmf=np.asarray(payload["cmf_xyz"], dtype=np.float64),
        d65=np.asarray(payload["d65"], dtype=np.float64),
        reflectances=np.asarray(payload["reflectances"], dtype=np.float64),
        reflectance_source=list(payload["reflectance_source"]),
        illuminants=np.asarray(payload["illuminants"], dtype=np.float64),
        illuminant_type=list(payload["illuminant_type"]),
        illuminant_source=list(payload["illuminant_source"]),
    )


def xyz_matrix(lib: SpectralLibrary) -> np.ndarray:
    """(3, 47) matrix mapping spectra to XYZ, normalised so the visible equal-energy white has Y = 1."""
    return lib.cmf / float(lib.cmf[1] @ lib.visible_mask)


def spectra_to_xyz(spectra: np.ndarray, lib: SpectralLibrary) -> np.ndarray:
    return np.atleast_2d(spectra) @ xyz_matrix(lib).T


def white_xyz(lib: SpectralLibrary) -> np.ndarray:
    """Reference white for CIELAB: the visible equal-energy spectrum (Y = 1)."""
    return spectra_to_xyz(lib.visible_mask[None, :], lib)[0]


def xyz_to_lab(xyz: np.ndarray, white: np.ndarray) -> np.ndarray:
    t = np.clip(np.asarray(xyz, dtype=np.float64) / white, 0.0, None)
    d = 6.0 / 29.0
    f = np.where(t > d**3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def delta_e94(lab_a: np.ndarray, lab_b: np.ndarray) -> np.ndarray:
    """CIE94 (graphic arts) colour difference, lab_a is the reference."""
    d_l = lab_a[..., 0] - lab_b[..., 0]
    c1 = np.hypot(lab_a[..., 1], lab_a[..., 2])
    c2 = np.hypot(lab_b[..., 1], lab_b[..., 2])
    d_c = c1 - c2
    d_h2 = np.maximum((lab_a[..., 1] - lab_b[..., 1]) ** 2 + (lab_a[..., 2] - lab_b[..., 2]) ** 2 - d_c**2, 0.0)
    return np.sqrt(d_l**2 + (d_c / (1 + 0.045 * c1)) ** 2 + d_h2 / (1 + 0.015 * c1) ** 2)


def reflectance_rgb_matrix(lib: SpectralLibrary) -> np.ndarray:
    """(3, 47) linear map from a reflectance spectrum to its linear-sRGB albedo.

    Albedo = linear sRGB of the reflectance under D65, divided channelwise by
    the linear sRGB of D65 itself (a perfect white reflector maps to 1, 1, 1).
    """
    m = XYZ_TO_LINEAR_SRGB @ xyz_matrix(lib)
    rgb_d65 = m @ lib.d65
    return (m * lib.d65[None, :]) / rgb_d65[:, None]


def illuminant_rgb_matrix(lib: SpectralLibrary) -> np.ndarray:
    """(3, 47) linear map from an emission spectrum to its linear-sRGB radiance."""
    return XYZ_TO_LINEAR_SRGB @ xyz_matrix(lib)


def asset_rgb(spectra: np.ndarray, kind: str, lib: SpectralLibrary) -> np.ndarray:
    """Legacy RGB value of a spectral asset, as seen by the RGB-upsampling test.

    ``kind`` is "reflectance" or "illuminant". Values are clipped at zero
    because stored RGB textures and light colours cannot be negative.
    """
    mat = reflectance_rgb_matrix(lib) if kind == "reflectance" else illuminant_rgb_matrix(lib)
    return np.clip(np.atleast_2d(spectra) @ mat.T, 0.0, None)
