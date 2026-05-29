#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from data.spectral_common import (  # noqa: E402
    WAVELENGTHS,
    color_matching_functions,
    latent_band_basis,
    make_dataset,
    make_multibounce_chains,
    make_product_pairs,
    summarize_color_error,
)
from method.hadamard_codec import NonnegativeLinearHadamardCodec, cosine_shaped_mse  # noqa: E402


def _sample_batch(rng: np.random.Generator, reflectances: np.ndarray, illuminants: np.ndarray, batch_size: int):
    r = reflectances[rng.integers(0, len(reflectances), size=batch_size)]
    l = illuminants[rng.integers(0, len(illuminants), size=batch_size)]
    return torch.from_numpy(r), torch.from_numpy(l)


def _color_loss(cmf: torch.Tensor, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return F.mse_loss(pred @ cmf.T, target @ cmf.T)


def _loss_terms(codec: NonnegativeLinearHadamardCodec, cmf: torch.Tensor, r: torch.Tensor, l: torch.Tensor, args: argparse.Namespace):
    target = r * l
    pred = codec.product_spectrum(r, l)
    z_prod = codec.product_code(r, l)
    loss_e2e = cosine_shaped_mse(pred, target)
    loss_rec = F.mse_loss(codec(r), r) + F.mse_loss(codec(l), l)
    loss_code = F.mse_loss(z_prod, codec.encode(target))
    loss_col = _color_loss(cmf, pred, target)
    loss = (
        args.lambda_e2e * loss_e2e
        + args.lambda_rec * loss_rec
        + args.lambda_code * loss_code
        + args.lambda_col * loss_col
    )
    return loss, {
        "e2e": float(loss_e2e.detach().cpu()),
        "rec": float(loss_rec.detach().cpu()),
        "code": float(loss_code.detach().cpu()),
        "color": float(loss_col.detach().cpu()),
    }


def train(args: argparse.Namespace) -> NonnegativeLinearHadamardCodec:
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    ds = make_dataset(seed=args.seed)
    device = torch.device(args.device)
    codec = NonnegativeLinearHadamardCodec(n_wavelengths=WAVELENGTHS.size, k=args.k).to(device)
    if args.band_init and args.k == 6:
        codec.reset_from_basis(latent_band_basis())
    opt = torch.optim.Adam(codec.parameters(), lr=args.lr)
    cmf = torch.from_numpy(color_matching_functions()).to(device)
    reflectances_all = ds.reflectance_train.astype(np.float32)
    illuminants_all = ds.illumination_train.astype(np.float32)
    r_cut = int(0.85 * len(reflectances_all))
    l_cut = int(0.85 * len(illuminants_all))
    reflectances, reflectances_val = reflectances_all[:r_cut], reflectances_all[r_cut:]
    illuminants, illuminants_val = illuminants_all[:l_cut], illuminants_all[l_cut:]
    steps_per_epoch = max(1, len(reflectances) // args.batch_size)
    best = float("inf")
    best_state = {k: v.detach().cpu().clone() for k, v in codec.state_dict().items()}
    patience = 0
    for epoch in range(args.epochs):
        codec.train()
        for _ in range(steps_per_epoch):
            r, l = _sample_batch(rng, reflectances, illuminants, args.batch_size)
            loss, _ = _loss_terms(codec, cmf, r.to(device), l.to(device), args)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
        codec.eval()
        with torch.no_grad():
            r_val, l_val = _sample_batch(rng, reflectances_val, illuminants_val, min(512, args.batch_size * 4))
            val_loss, _ = _loss_terms(codec, cmf, r_val.to(device), l_val.to(device), args)
            value = float(val_loss.detach().cpu())
        if value < best - 1e-7:
            best = value
            best_state = {k: v.detach().cpu().clone() for k, v in codec.state_dict().items()}
            patience = 0
        else:
            patience += 1
        if args.early_stop and patience > args.early_stop:
            break
    codec.load_state_dict(best_state)
    return codec.cpu()


def _predict_product(codec: NonnegativeLinearHadamardCodec, kind: str, count: int) -> dict:
    r, l = make_product_pairs(kind, count=count)
    with torch.no_grad():
        pred = codec.product_spectrum(torch.from_numpy(r), torch.from_numpy(l)).numpy()
    target = r * l
    metrics = summarize_color_error(pred, target)
    return {
        "reflectance": r.tolist(),
        "illumination": l.tolist(),
        "target_spectrum": target.tolist(),
        "pred_spectrum": pred.tolist(),
        "metrics_preview": metrics,
    }


def _predict_multibounce(codec: NonnegativeLinearHadamardCodec, kind: str, count: int) -> dict:
    reflectances, illumination = make_multibounce_chains(kind, count=count, bounces=3)
    current_spec = illumination.copy()
    with torch.no_grad():
        current_code = codec.encode(torch.from_numpy(illumination))
        for bounce in range(reflectances.shape[1]):
            r = torch.from_numpy(reflectances[:, bounce, :])
            current_spec = current_spec * reflectances[:, bounce, :]
            current_code = current_code * codec.encode(r)
        pred = codec.decode(current_code).numpy()
    metrics = summarize_color_error(pred, current_spec)
    return {
        "reflectance_chain": reflectances.tolist(),
        "illumination": illumination.tolist(),
        "target_spectrum": current_spec.tolist(),
        "pred_spectrum": pred.tolist(),
        "metrics_preview": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/hadamard_k6")
    parser.add_argument("--k", type=int, default=6)
    parser.add_argument("--epochs", type=int, default=180)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=260218741)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--lambda-e2e", type=float, default=0.5)
    parser.add_argument("--lambda-rec", type=float, default=0.75)
    parser.add_argument("--lambda-code", type=float, default=1.0)
    parser.add_argument("--lambda-col", type=float, default=0.5)
    parser.add_argument("--early-stop", type=int, default=0)
    parser.add_argument("--eval-count", type=int, default=240)
    parser.add_argument("--band-init", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    codec = train(args)
    torch.save({"state_dict": codec.state_dict(), "k": args.k}, out / "codec.pt")
    payload = {
        "method": "hadamard_k6",
        "k": args.k,
        "render_passes": args.k // 3,
        "spectral_samples": int(WAVELENGTHS.size),
        "experiments": {
            "spectral_product_broadband": _predict_product(codec, "broadband", args.eval_count),
            "spectral_product_narrowband": _predict_product(codec, "narrowband", args.eval_count),
            "multibounce_narrowband": _predict_multibounce(codec, "narrowband", max(80, args.eval_count // 2)),
        },
    }
    (out / "predictions.json").write_text(json.dumps(payload))
    print(json.dumps({k: v["metrics_preview"] for k, v in payload["experiments"].items()}, indent=2))


if __name__ == "__main__":
    main()
