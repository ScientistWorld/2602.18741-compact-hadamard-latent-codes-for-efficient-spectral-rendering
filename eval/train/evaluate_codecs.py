#!/usr/bin/env python3
"""Training-slice evaluator for compact spectral-rendering codecs (public).

Every directory ``outputs/<method>/`` is one submitted method. Its
``codec.json`` describes the method's spectral encoders, decoder and optional
RGB upsamplers as small feed-forward networks (see briefing/evaluation.md).
This evaluator owns everything else: the rendered instances (built here from
the public training spectra in data/spectra_train.json), the latent-space
renderer (per-channel products, scaling and sums, with negative codes clamped
to zero as in an RGB renderer), exposure, colorimetry and the metrics. The
hidden test slice runs the same protocol on held-out spectra.

Validity gates (failing any gives the worst value in every metric):
  * latent width 1..6 channels (at most two RGB render passes),
  * well-formed networks with finite weights and matching shapes,
  * finite codes and decoded spectra on every test input.
A missing or malformed upsampler fails only the RGB-upsampling experiment.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET_FILE = ROOT / "data" / "spectra_train.json"
OUTPUTS_DIR = ROOT / "outputs"
CODEC_FILE = "codec.json"  # read from outputs/<method>/codec.json
SLICE = "train"
SEED = 11_235_813_21

N_WAVE = 47
MAX_LATENT = 6
MAX_PARAMS = 2_000_000
DE_CAP = 100.0
NRMSE_CAP = 2.0

EXPERIMENTS = {
    "spectral_product_broadband": ["mean_delta_e94", "p95_delta_e94", "spectral_nrmse"],
    "spectral_product_narrowband": ["mean_delta_e94", "p95_delta_e94", "spectral_nrmse"],
    "multibounce_narrowband": ["mean_delta_e94", "p95_delta_e94", "spectral_nrmse"],
    "multibounce_proxy": ["mean_delta_e94_1bounce", "mean_delta_e94_2bounce", "mean_delta_e94_3bounce"],
    "rendered_scenes": ["mean_delta_e94", "p95_delta_e94", "spectral_nrmse"],
    "rgb_upsampling": ["mean_delta_e94", "p95_delta_e94", "spectral_nrmse"],
}
WORST = {
    "mean_delta_e94": DE_CAP,
    "p95_delta_e94": DE_CAP,
    "spectral_nrmse": NRMSE_CAP,
    "mean_delta_e94_1bounce": DE_CAP,
    "mean_delta_e94_2bounce": DE_CAP,
    "mean_delta_e94_3bounce": DE_CAP,
}

N_PAIRS = 4000
N_CHAINS = 3000
N_SCENES = 300
PIXELS_PER_SCENE = 48
LIGHTS_PER_SCENE = 2
MATERIALS_PER_SCENE = 10
MAX_DEPTH = 8
PATHS_PER_DEPTH = 2

XYZ_TO_LINEAR_SRGB = np.array(
    [[3.2404542, -1.5371385, -0.4985314], [-0.9692660, 1.8760108, 0.0415560], [0.0556434, -0.2040259, 1.0572252]]
)


class CodecError(Exception):
    pass


# ----------------------------------------------------------------------------
# Assets and colorimetry


@dataclass
class Assets:
    mask: np.ndarray
    xyz_mat: np.ndarray
    white: np.ndarray
    d65: np.ndarray
    refl: np.ndarray
    illum: np.ndarray
    broad: np.ndarray
    narrow: np.ndarray


def load_assets(path: Path) -> Assets:
    payload = json.loads(path.read_text())
    mask = np.asarray(payload["visible_mask"], dtype=np.float64)
    cmf = np.asarray(payload["cmf_xyz"], dtype=np.float64)
    xyz_mat = cmf / float(cmf[1] @ mask)
    types = np.asarray(payload["illuminant_type"])
    return Assets(
        mask=mask,
        xyz_mat=xyz_mat,
        white=xyz_mat @ mask,
        d65=np.asarray(payload["d65"], dtype=np.float64),
        refl=np.asarray(payload["reflectances"], dtype=np.float64),
        illum=np.asarray(payload["illuminants"], dtype=np.float64),
        broad=np.flatnonzero(types == "broadband"),
        narrow=np.flatnonzero(types == "narrowband"),
    )


def to_lab(spectra: np.ndarray, a: Assets) -> np.ndarray:
    t = np.clip((spectra @ a.xyz_mat.T) / a.white, 0.0, None)
    d = 6.0 / 29.0
    f = np.where(t > d**3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def delta_e94(ref: np.ndarray, test: np.ndarray) -> np.ndarray:
    d_l = ref[..., 0] - test[..., 0]
    c1 = np.hypot(ref[..., 1], ref[..., 2])
    c2 = np.hypot(test[..., 1], test[..., 2])
    d_c = c1 - c2
    d_h2 = np.maximum((ref[..., 1] - test[..., 1]) ** 2 + (ref[..., 2] - test[..., 2]) ** 2 - d_c**2, 0.0)
    return np.sqrt(d_l**2 + (d_c / (1 + 0.045 * c1)) ** 2 + d_h2 / (1 + 0.015 * c1) ** 2)


def exposure_for(spectra: np.ndarray, a: Assets) -> np.ndarray:
    """Scale that brings the strongest normalised tristimulus channel to 1."""
    rel = (spectra @ a.xyz_mat.T) / a.white
    return 1.0 / np.maximum(rel.max(axis=-1), 1e-12)


def error_stats(pred: np.ndarray, target: np.ndarray, a: Assets) -> tuple[np.ndarray, np.ndarray]:
    de = delta_e94(to_lab(target, a), to_lab(pred, a))
    de = np.where(np.isfinite(de), np.minimum(de, DE_CAP), DE_CAP)
    num = np.linalg.norm(pred - target, axis=-1)
    den = np.maximum(np.linalg.norm(target, axis=-1), 1e-12)
    nrmse = np.where(np.isfinite(num), np.minimum(num / den, NRMSE_CAP), NRMSE_CAP)
    return de, nrmse


def summarize(pred: np.ndarray, target: np.ndarray, a: Assets) -> dict[str, float]:
    de, nrmse = error_stats(pred, target, a)
    return {
        "mean_delta_e94": float(np.mean(de)),
        "p95_delta_e94": float(np.percentile(de, 95)),
        "spectral_nrmse": float(np.mean(nrmse)),
    }


# ----------------------------------------------------------------------------
# Codec networks


def _sigmoid(x):
    return 0.5 * (1.0 + np.tanh(0.5 * x))


ACTIVATIONS = {
    "identity": lambda x, beta: x,
    "linear": lambda x, beta: x,
    "relu": lambda x, beta: np.maximum(x, 0.0),
    "leaky_relu": lambda x, beta: np.where(x > 0, x, 0.01 * x),
    "softplus": lambda x, beta: np.logaddexp(0.0, beta * x) / beta,
    "silu": lambda x, beta: x * _sigmoid(x),
    "sigmoid": lambda x, beta: _sigmoid(x),
    "tanh": lambda x, beta: np.tanh(x),
    "elu": lambda x, beta: np.where(x > 0, x, np.expm1(np.minimum(x, 0.0))),
    "gelu": lambda x, beta: 0.5 * x * (1.0 + np.tanh(0.7978845608 * (x + 0.044715 * x**3))),
    "abs": lambda x, beta: np.abs(x),
    "square": lambda x, beta: x * x,
}


def parse_net(spec, name: str, in_dim: int):
    if spec is None:
        raise CodecError(f"{name}: missing")
    if isinstance(spec, dict) and "layers" in spec:
        layer_specs = spec["layers"]
    elif isinstance(spec, list) and spec and all(isinstance(item, dict) for item in spec):
        layer_specs = spec
    else:
        layer_specs = [{"weight": spec, "activation": "identity"}]
    if not isinstance(layer_specs, list) or not layer_specs:
        raise CodecError(f"{name}: no layers")
    layers = []
    dim = in_dim
    total = 0
    for i, layer in enumerate(layer_specs):
        if not isinstance(layer, dict) or "weight" not in layer:
            raise CodecError(f"{name}[{i}]: layer needs a 'weight' matrix")
        try:
            weight = np.asarray(layer["weight"], dtype=np.float64)
            bias = np.zeros(weight.shape[0]) if layer.get("bias") is None else np.asarray(layer["bias"], dtype=np.float64)
            beta = float(layer.get("beta", 1.0))
        except (TypeError, ValueError, IndexError) as exc:
            raise CodecError(f"{name}[{i}]: malformed numbers ({exc})") from None
        if weight.ndim != 2 or weight.shape[0] < 1 or weight.shape[1] != dim:
            raise CodecError(f"{name}[{i}]: weight shape {weight.shape} does not accept input width {dim}")
        if bias.shape != (weight.shape[0],):
            raise CodecError(f"{name}[{i}]: bias shape {bias.shape} != ({weight.shape[0]},)")
        act = layer.get("activation", "identity")
        if act not in ACTIVATIONS:
            raise CodecError(f"{name}[{i}]: unknown activation {act!r}")
        if not (np.all(np.isfinite(weight)) and np.all(np.isfinite(bias)) and math.isfinite(beta) and beta > 0):
            raise CodecError(f"{name}[{i}]: non-finite parameters")
        total += weight.size + bias.size
        layers.append((weight, bias, act, beta))
        dim = weight.shape[0]
    if total > MAX_PARAMS:
        raise CodecError(f"{name}: {total} parameters exceed {MAX_PARAMS}")
    return layers, dim


def run_net(layers, x: np.ndarray, name: str) -> np.ndarray:
    with np.errstate(all="ignore"):
        for weight, bias, act, beta in layers:
            x = ACTIVATIONS[act](x @ weight.T + bias, beta)
    if not np.all(np.isfinite(x)):
        raise CodecError(f"{name}: non-finite output")
    return x


@dataclass
class Codec:
    k: int
    enc_r: list
    enc_l: list
    dec: list
    up_r: list | None
    up_l: list | None
    up_error: str | None

    def decode(self, latent: np.ndarray) -> np.ndarray:
        shape = latent.shape
        out = run_net(self.dec, latent.reshape(-1, self.k), "decoder")
        return np.clip(out, 0.0, None).reshape(*shape[:-1], N_WAVE)


def load_codec(method_dir: Path) -> Codec:
    path = method_dir / CODEC_FILE
    if not path.is_file():
        raise CodecError(f"missing {CODEC_FILE}")
    try:
        spec = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise CodecError(f"unreadable {CODEC_FILE}: {exc}") from None
    if not isinstance(spec, dict):
        raise CodecError(f"{CODEC_FILE} must hold a JSON object")
    enc_r, k_r = parse_net(spec.get("encoder_reflectance", spec.get("encoder")), "encoder_reflectance", N_WAVE)
    enc_l, k_l = parse_net(spec.get("encoder_illuminant", spec.get("encoder")), "encoder_illuminant", N_WAVE)
    if k_r != k_l:
        raise CodecError(f"encoders disagree on latent width ({k_r} vs {k_l})")
    if not 1 <= k_r <= MAX_LATENT:
        raise CodecError(f"latent width {k_r} is outside 1..{MAX_LATENT} (two RGB passes)")
    dec, out_dim = parse_net(spec.get("decoder"), "decoder", k_r)
    if out_dim != N_WAVE:
        raise CodecError(f"decoder outputs {out_dim} values, expected {N_WAVE}")
    up_r = up_l = None
    up_error = None
    up_r_spec = spec.get("upsampler_reflectance", spec.get("upsampler"))
    up_l_spec = spec.get("upsampler_illuminant", spec.get("upsampler"))
    if up_r_spec is None or up_l_spec is None:
        up_error = "no RGB upsampler supplied"
    else:
        try:
            up_r, kr = parse_net(up_r_spec, "upsampler_reflectance", 3)
            up_l, kl = parse_net(up_l_spec, "upsampler_illuminant", 3)
            if kr != k_r or kl != k_r:
                raise CodecError(f"upsampler width ({kr}, {kl}) != latent width {k_r}")
        except CodecError as exc:
            up_r = up_l = None
            up_error = str(exc)
    return Codec(k_r, enc_r, enc_l, dec, up_r, up_l, up_error)


# ----------------------------------------------------------------------------
# Fixed instances (depend only on the assets and the slice seed)


@dataclass
class Instances:
    pairs_broad: tuple
    pairs_narrow: tuple
    chains_narrow: tuple
    proxy: tuple
    scenes: dict
    upsample_pairs: tuple


def _rng(i: int) -> np.random.Generator:
    return np.random.default_rng([SEED, i])


def build_instances(a: Assets) -> Instances:
    nr = len(a.refl)

    def pairs(pool, rng, n):
        return rng.integers(nr, size=n), pool[rng.integers(len(pool), size=n)]

    def mixed_lights(rng, n):
        half = n // 2
        return np.concatenate([a.broad[rng.integers(len(a.broad), size=half)], a.narrow[rng.integers(len(a.narrow), size=n - half)]])

    rng = _rng(1)
    pairs_broad = pairs(a.broad, rng, N_PAIRS)
    rng = _rng(2)
    pairs_narrow = pairs(a.narrow, rng, N_PAIRS)
    rng = _rng(3)
    chains_narrow = (rng.integers(nr, size=(N_CHAINS, 3)), a.narrow[rng.integers(len(a.narrow), size=N_CHAINS)])
    rng = _rng(4)
    proxy = (rng.integers(nr, size=(N_CHAINS, 3)), mixed_lights(rng, N_CHAINS))
    rng = _rng(6)
    upsample_pairs = pairs(a.broad, rng, N_PAIRS)  # broadband scenes, as in the paper's RGB-asset tests

    rng = _rng(5)
    s, p, m, d = N_SCENES, PIXELS_PER_SCENE, MATERIALS_PER_SCENE, MAX_DEPTH
    depth_pattern = np.array([1] + [dd for dd in range(2, d + 1) for _ in range(PATHS_PER_DEPTH)])
    depth = np.tile(depth_pattern, LIGHTS_PER_SCENE)
    slot = np.repeat(np.arange(LIGHTS_PER_SCENE), len(depth_pattern))
    t = len(depth)
    narrow_pick = rng.random((s, LIGHTS_PER_SCENE)) < 0.5
    broad_ids = a.broad[rng.integers(len(a.broad), size=(s, LIGHTS_PER_SCENE))]
    narrow_ids = a.narrow[rng.integers(len(a.narrow), size=(s, LIGHTS_PER_SCENE))]
    scene_lights = np.where(narrow_pick, narrow_ids, broad_ids)
    intensity = np.exp(rng.uniform(np.log(0.3), np.log(3.0), size=(s, LIGHTS_PER_SCENE)))
    scene_mats = np.stack([rng.choice(nr, size=m, replace=False) for _ in range(s)])
    local = rng.integers(m, size=(s, p, t, d))
    local[..., 0] = rng.integers(m, size=(s, p))[..., None]
    mats = scene_mats[np.arange(s)[:, None, None, None], local]
    active = np.arange(d)[None, :] < depth[:, None]
    geometry = rng.uniform(0.0, 1.0, size=(s, p, t)) * (rng.random((s, p, t)) > 0.2)
    bounce = rng.uniform(0.25, 0.75, size=(s, p, t, d))
    bounce = np.where(active[None, None, :, :] & (np.arange(d) >= 1)[None, None, None, :], bounce, 1.0)
    weight = geometry * bounce.prod(axis=-1) * intensity[:, slot][:, None, :]
    light_ids = np.broadcast_to(scene_lights[:, slot][:, None, :], (s, p, t))
    scenes = {"mats": mats, "active": active, "weight": weight, "lights": light_ids}
    return Instances(pairs_broad, pairs_narrow, chains_narrow, proxy, scenes, upsample_pairs)


def render_scenes(scenes: dict, refl_rep: np.ndarray, illum_rep: np.ndarray) -> np.ndarray:
    """Sum of weighted light paths per pixel, in whatever representation is given."""
    mats, active, weight, lights = scenes["mats"], scenes["active"], scenes["weight"], scenes["lights"]
    out = []
    for lo in range(0, mats.shape[0], 25):
        hi = lo + 25
        x = weight[lo:hi, ..., None] * illum_rep[lights[lo:hi]]
        for dd in range(mats.shape[-1]):
            factor = refl_rep[mats[lo:hi, :, :, dd]]
            x = x * np.where(active[None, None, :, dd, None], factor, 1.0)
        out.append(x.sum(axis=2))
    return np.concatenate(out)


@dataclass
class Targets:
    pairs_broad: np.ndarray
    pairs_narrow: np.ndarray
    chains_narrow: np.ndarray
    proxy: list
    scenes: np.ndarray
    scene_exposure: np.ndarray
    upsample: np.ndarray
    light_exposure: np.ndarray


def build_targets(a: Assets, inst: Instances) -> Targets:
    light_exposure = exposure_for(a.illum, a)
    r, l = inst.chains_narrow
    chains = a.illum[l] * a.refl[r[:, 0]] * a.refl[r[:, 1]] * a.refl[r[:, 2]]
    r, l = inst.proxy
    proxy = []
    cur = a.illum[l].copy()
    for b in range(3):
        cur = cur * a.refl[r[:, b]]
        proxy.append(cur.copy())
    scenes = render_scenes(inst.scenes, a.refl, a.illum)
    rel = (scenes @ a.xyz_mat.T / a.white).max(axis=-1)
    scene_exposure = 0.8 / np.maximum(np.quantile(rel, 0.9, axis=1), 1e-12)
    return Targets(
        pairs_broad=a.refl[inst.pairs_broad[0]] * a.illum[inst.pairs_broad[1]],
        pairs_narrow=a.refl[inst.pairs_narrow[0]] * a.illum[inst.pairs_narrow[1]],
        chains_narrow=chains,
        proxy=proxy,
        scenes=scenes,
        scene_exposure=scene_exposure,
        upsample=a.refl[inst.upsample_pairs[0]] * a.illum[inst.upsample_pairs[1]],
        light_exposure=light_exposure,
    )


# ----------------------------------------------------------------------------
# Scoring


def worst(exp: str) -> dict[str, float]:
    return {metric: WORST[metric] for metric in EXPERIMENTS[exp]}


def score_codec(codec: Codec, a: Assets, inst: Instances, tgt: Targets) -> dict[str, dict[str, float]]:
    z_r = np.clip(run_net(codec.enc_r, a.refl, "encoder_reflectance"), 0.0, None)
    z_l = np.clip(run_net(codec.enc_l, a.illum, "encoder_illuminant"), 0.0, None)
    res: dict[str, dict[str, float]] = {}

    def scaled(pred, target, light_ids):
        e = tgt.light_exposure[light_ids][:, None]
        return summarize(pred * e, target * e, a)

    for exp, (r, l), target in [
        ("spectral_product_broadband", inst.pairs_broad, tgt.pairs_broad),
        ("spectral_product_narrowband", inst.pairs_narrow, tgt.pairs_narrow),
    ]:
        res[exp] = scaled(codec.decode(z_r[r] * z_l[l]), target, l)

    r, l = inst.chains_narrow
    latent = z_l[l] * z_r[r[:, 0]] * z_r[r[:, 1]] * z_r[r[:, 2]]
    res["multibounce_narrowband"] = scaled(codec.decode(latent), tgt.chains_narrow, l)

    r, l = inst.proxy
    latent = z_l[l]
    proxy = {}
    for b in range(3):
        latent = latent * z_r[r[:, b]]
        de, _ = error_stats(codec.decode(latent), tgt.proxy[b], a)
        proxy[f"mean_delta_e94_{b + 1}bounce"] = float(np.mean(de))
    res["multibounce_proxy"] = proxy

    latent = render_scenes(inst.scenes, z_r, z_l)
    pred = codec.decode(latent)
    e = tgt.scene_exposure[:, None, None]
    res["rendered_scenes"] = summarize((pred * e).reshape(-1, N_WAVE), (tgt.scenes * e).reshape(-1, N_WAVE), a)

    if codec.up_error is None:
        rgb_r = np.clip(a.refl @ reflectance_rgb_matrix(a).T, 0.0, None)
        rgb_l = np.clip(a.illum @ illuminant_rgb_matrix(a).T, 0.0, None)
        u_r = np.clip(run_net(codec.up_r, rgb_r, "upsampler_reflectance"), 0.0, None)
        u_l = np.clip(run_net(codec.up_l, rgb_l, "upsampler_illuminant"), 0.0, None)
        r, l = inst.upsample_pairs
        res["rgb_upsampling"] = scaled(codec.decode(u_r[r] * u_l[l]), tgt.upsample, l)
    else:
        res["rgb_upsampling"] = worst("rgb_upsampling")
    return res


def reflectance_rgb_matrix(a: Assets) -> np.ndarray:
    m = XYZ_TO_LINEAR_SRGB @ a.xyz_mat
    rgb_d65 = m @ a.d65
    return (m * a.d65[None, :]) / rgb_d65[:, None]


def illuminant_rgb_matrix(a: Assets) -> np.ndarray:
    return XYZ_TO_LINEAR_SRGB @ a.xyz_mat


def discover_methods(outputs_dir: Path) -> list[Path]:
    if not outputs_dir.is_dir():
        return []
    return sorted(p for p in outputs_dir.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def evaluate(method_dirs: list[Path], assets_path: Path) -> dict:
    a = load_assets(assets_path)
    inst = build_instances(a)
    tgt = build_targets(a, inst)
    scores: dict = {"experiments": {exp: {"results": {}} for exp in EXPERIMENTS}, "_diagnostics": {"slice": SLICE, "methods": {}}}
    for method_dir in method_dirs:
        name = method_dir.name
        diag: dict = {}
        try:
            codec = load_codec(method_dir)
            diag.update(latent_channels=codec.k, render_passes=int(math.ceil(codec.k / 3)))
            res = score_codec(codec, a, inst, tgt)
            diag["status"] = "ok" if codec.up_error is None else "ok_without_upsampling"
            if codec.up_error is not None:
                diag["upsampling_error"] = codec.up_error
        except Exception as exc:  # any malformed submission scores as failed, never crashes the run
            res = {exp: worst(exp) for exp in EXPERIMENTS}
            diag.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        for exp in EXPERIMENTS:
            values = {m: float(res[exp][m]) for m in EXPERIMENTS[exp]}
            if not all(math.isfinite(v) for v in values.values()):
                values = worst(exp)
            scores["experiments"][exp]["results"][name] = values
        scores["_diagnostics"]["methods"][name] = diag
    return scores


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="*", help="Method directories (default: every directory under outputs/).")
    parser.add_argument("--outputs-dir", default=str(OUTPUTS_DIR))
    parser.add_argument("--output", default=str(ROOT / "scoring" / "scores_train.json"))
    args = parser.parse_args()
    runs = [Path(p) for p in args.runs] if args.runs else discover_methods(Path(args.outputs_dir))
    scores = evaluate(runs, ASSET_FILE)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scores, indent=2, sort_keys=True))
    print(json.dumps(scores, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
