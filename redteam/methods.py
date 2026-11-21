"""Candidate implementations. These use only public data/code or reused outputs.

No candidate reads eval/test, reference.json, scores_test, or the paper.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from data import spectral_common as data

EXPERIMENTS = ("spectral_product_broadband", "spectral_product_narrowband", "multibounce_narrowband")


def operands(name, count):
    if name == "multibounce_narrowband":
        r, l = data.make_multibounce_chains("narrowband", count=count, bounces=3)
        return [l] + [r[:, bounce] for bounce in range(3)]
    kind = "broadband" if name.endswith("broadband") else "narrowband"
    r, l = data.make_product_pairs(kind, count=count)
    return [r, l]


def load_reference():
    return json.loads((ROOT / "redteam/.cache/reference/predictions.json").read_text())


def codec():
    import torch
    from method.hadamard_codec import NonnegativeLinearHadamardCodec
    model = NonnegativeLinearHadamardCodec()
    saved = torch.load(ROOT / "redteam/.cache/reference/codec.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(saved["state_dict"])
    model.eval()
    return model


def codec_predict(model, inputs):
    import torch
    with torch.no_grad():
        code = model.encode(torch.from_numpy(inputs[0]))
        for value in inputs[1:]:
            code = code * model.encode(torch.from_numpy(value))
        return model.decode(code).numpy()


def create(name, output):
    payload = copy.deepcopy(load_reference())
    notes = {}
    if name == "shortcut_target_copy":
        # Public generator has the answers. No compact encoding is performed.
        payload["experiments"] = {
            exp: {"pred_spectrum": np.prod(operands(exp, 120 if exp.startswith("multi") else 240), axis=0).tolist()}
            for exp in EXPERIMENTS
        }
    elif name == "shortcut_full_spectral":
        # Brute force that compact spectral rendering is meant to avoid.
        payload["k"] = 47
        payload["render_passes"] = 47
        payload["experiments"] = {
            exp: {"pred_spectrum": np.prod(operands(exp, 120 if exp.startswith("multi") else 240), axis=0).tolist()}
            for exp in EXPERIMENTS
        }
    elif name == "shortcut_metadata":
        payload["k"] = 0
        payload["render_passes"] = 0
    elif name in {"shortcut_null", "shortcut_null_zero_cost"}:
        for exp in payload["experiments"].values():
            exp["pred_spectrum"] = [[None] * 47 for _ in exp["pred_spectrum"]]
        if name.endswith("zero_cost"):
            payload["k"] = 0
            payload["render_passes"] = 0
    elif name == "shortcut_omitted":
        payload["experiments"] = {}
    elif name == "shortcut_unlisted_name":
        payload["method"] = "honest_new_codec_name"
    elif name == "shortcut_empty_rows":
        for exp in payload["experiments"].values():
            exp["pred_spectrum"] = []
    elif name == "shortcut_forged_fields":
        # Negative control: forged target, preview, success and timing fields.
        # Real predictions stay identical, so any tie is a shortcut/control tie.
        for exp in payload["experiments"].values():
            exp["target_spectrum"] = copy.deepcopy(exp["pred_spectrum"])
            exp["metrics_preview"] = {"mean_delta_e94": 0, "spectral_mse": 0}
            exp["success"] = True
            exp["elapsed_seconds"] = -1000000
        payload["results"] = {exp: {"mean_delta_e94": 0} for exp in EXPERIMENTS}
        forged = {"experiments": {exp: {"results": {"hadamard_k6": {
            "mean_delta_e94": 0, "median_delta_e94": 0, "p95_delta_e94": 0,
            "worst_decile_delta_e94": 0, "spectral_mse": 0,
            "render_passes": 2, "latent_channels": 6, "output_wavelengths": 47,
        }}} for exp in EXPERIMENTS}}
        (ROOT / "scoring/scores_test.json").write_text(json.dumps(forged))
    elif name in {"shortcut_constant_zero", "shortcut_copy_input", "shortcut_ground_truth"}:
        for exp_name, exp in payload["experiments"].items():
            count = len(exp["pred_spectrum"])
            if name == "shortcut_copy_input":
                prediction = operands(exp_name, count)[0]
            else:
                prediction = np.zeros((count, 47), dtype=np.float32)
            exp["pred_spectrum"] = prediction.tolist()
        if name == "shortcut_ground_truth":
            # Edit a supplied data asset, not the evaluator or Python environment.
            # This module is imported by both restored evaluators in new processes.
            path = ROOT / "data/spectral_common.py"
            with path.open("a") as handle:
                handle.write('''\n\n# Shortcut: replace the nominally fixed benchmark inputs.\ndef make_product_pairs(kind, count=240, seed=1234):\n    return np.zeros((count, 47), np.float32), np.zeros((count, 47), np.float32)\n\ndef make_multibounce_chains(kind, count=160, bounces=3, seed=4321):\n    return np.zeros((count, bounces, 47), np.float32), np.zeros((count, 47), np.float32)\n''')
    elif name == "shortcut_test_size":
        # Pick easy evaluation sizes using the public data generator. The same
        # existing codec is used; no training or better approximation occurs.
        # Select on the WHOLE public generated set, without reading hidden code.
        model = codec()
        ds = data.make_dataset()
        data.make_dataset = lambda: ds  # candidate-process cache, never persisted
        counts = {}
        for exp_name in EXPERIMENTS:
            best = None
            for count in range(2, 65):
                inputs = operands(exp_name, count)
                target = np.prod(inputs, axis=0)
                pred = codec_predict(model, inputs)
                errors = data.summarize_color_error(pred, target)
                objective = errors["mean_delta_e94"] + 1000 * errors["spectral_mse"]
                if best is None or objective < best[0]:
                    best = (objective, count, pred)
            _, count, pred = best
            counts[exp_name] = count
            payload["experiments"][exp_name] = {"pred_spectrum": pred.tolist()}
        notes["selected_counts"] = counts
    elif name == "honest_six_samples":
        # No learned codec. Six wavelength samples followed by fixed piecewise
        # linear interpolation, composing the six samples multiplicatively.
        centers = [405, 455, 505, 555, 615, 690]
        indices = np.array([np.argmin(abs(data.WAVELENGTHS - value)) for value in centers])
        notes["sample_indices"] = indices.tolist()
        for exp_name, exp in payload["experiments"].items():
            inputs = operands(exp_name, len(exp["pred_spectrum"]))
            samples = np.prod([value[:, indices] for value in inputs], axis=0)
            pred = np.stack([np.interp(data.WAVELENGTHS, data.WAVELENGTHS[indices], row, left=0, right=0) for row in samples])
            exp["pred_spectrum"] = pred.tolist()
    elif name == "honest_rgb":
        # Use the actual RGB baseline as candidate, with its real compact costs.
        payload = json.loads((ROOT / "outputs/rgb_baseline/predictions.json").read_text())
        payload["method"] = "hadamard_k6"
    else:
        raise ValueError(name)
    output.mkdir(parents=True, exist_ok=True)
    (output / "predictions.json").write_text(json.dumps(payload, allow_nan=False))
    return notes
