#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from data.spectral_common import (  # noqa: E402
    WAVELENGTHS,
    color_matching_functions,
    make_dataset,
    make_product_pairs,
    spectra_to_xyz,
    summarize_color_error,
    xyz_to_lab,
)
from method.hadamard_codec import NonnegativeLinearHadamardCodec  # noqa: E402


class RGBToLatentUpsampler(nn.Module):
    """Paper's per-pixel RGB-to-latent MLP for legacy RGB assets."""

    def __init__(self, k: int = 6, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, hidden),
            nn.SiLU(),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, k),
        )

    def forward(self, rgb: torch.Tensor) -> torch.Tensor:
        return F.softplus(self.net(rgb))


def _torch_xyz_to_lab(xyz: torch.Tensor, white: torch.Tensor) -> torch.Tensor:
    ratio = xyz / white.clamp_min(1e-8)
    delta = 6.0 / 29.0
    f = torch.where(ratio > delta**3, torch.pow(ratio.clamp_min(1e-8), 1.0 / 3.0), ratio / (3 * delta**2) + 4.0 / 29.0)
    return torch.stack(
        [116.0 * f[..., 1] - 16.0, 500.0 * (f[..., 0] - f[..., 1]), 200.0 * (f[..., 1] - f[..., 2])],
        dim=-1,
    )


def _load_codec(path: Path, device: torch.device) -> NonnegativeLinearHadamardCodec:
    payload = torch.load(path, map_location=device)
    codec = NonnegativeLinearHadamardCodec(n_wavelengths=WAVELENGTHS.size, k=int(payload["k"])).to(device)
    codec.load_state_dict(payload["state_dict"])
    codec.eval()
    for param in codec.parameters():
        param.requires_grad_(False)
    return codec


def _prepare_training_data(codec: NonnegativeLinearHadamardCodec, seed: int, device: torch.device):
    ds = make_dataset(seed=seed)
    spectra = np.concatenate([ds.reflectance_train, ds.illumination_train], axis=0).astype(np.float32)
    rgb = spectra_to_xyz(spectra).astype(np.float32)
    with torch.no_grad():
        latent = codec.encode(torch.from_numpy(spectra).to(device)).cpu().numpy().astype(np.float32)
    split = int(0.85 * len(spectra))
    return rgb[:split], latent[:split], rgb[split:], latent[split:]


def train(args: argparse.Namespace) -> tuple[RGBToLatentUpsampler, NonnegativeLinearHadamardCodec]:
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    device = torch.device(args.device)
    codec = _load_codec(Path(args.codec), device)
    rgb_train, z_train, rgb_val, z_val = _prepare_training_data(codec, args.seed, device)
    model = RGBToLatentUpsampler(k=codec.k).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5, patience=200, min_lr=1e-6)
    cmf = torch.from_numpy(color_matching_functions()).to(device)
    white = torch.from_numpy(spectra_to_xyz(np.ones((1, WAVELENGTHS.size), dtype=np.float32))[0]).to(device)
    best = float("inf")
    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    for epoch in range(args.epochs):
        model.train()
        order = rng.permutation(len(rgb_train))
        for start in range(0, len(order), args.batch_size):
            idx = order[start : start + args.batch_size]
            rgb = torch.from_numpy(rgb_train[idx]).to(device)
            target_z = torch.from_numpy(z_train[idx]).to(device)
            pred_z = model(rgb)
            latent_loss = F.mse_loss(pred_z, target_z) + args.lambda_max_abs * (pred_z - target_z).abs().amax(dim=-1).mean()
            pred_lab = _torch_xyz_to_lab(codec.decode(pred_z) @ cmf.T, white)
            target_lab = _torch_xyz_to_lab(codec.decode(target_z) @ cmf.T, white)
            color_loss = torch.linalg.vector_norm(pred_lab - target_lab, dim=-1).mean()
            loss = latent_loss + args.lambda_color * color_loss
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        model.eval()
        with torch.no_grad():
            rgb = torch.from_numpy(rgb_val).to(device)
            target_z = torch.from_numpy(z_val).to(device)
            pred_z = model(rgb)
            val = F.mse_loss(pred_z, target_z) + args.lambda_max_abs * (pred_z - target_z).abs().amax(dim=-1).mean()
            value = float(val.detach().cpu())
        scheduler.step(value)
        if value < best:
            best = value
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return model.cpu(), codec.cpu()


def _predict_rgb_asset_products(model: RGBToLatentUpsampler, codec: NonnegativeLinearHadamardCodec, kind: str, count: int) -> dict:
    reflectance, illumination = make_product_pairs(kind, count=count)
    r_rgb = torch.from_numpy(spectra_to_xyz(reflectance).astype(np.float32))
    l_rgb = torch.from_numpy(spectra_to_xyz(illumination).astype(np.float32))
    with torch.no_grad():
        z_r = model(r_rgb).view(-1, codec.k // 3, 3)
        z_l = model(l_rgb).view(-1, codec.k // 3, 3)
        pred = codec.decode((z_r * z_l).view(-1, codec.k)).numpy()
    target = reflectance * illumination
    return {
        "reflectance_rgb": r_rgb.numpy().tolist(),
        "illumination_rgb": l_rgb.numpy().tolist(),
        "target_spectrum": target.tolist(),
        "pred_spectrum": pred.tolist(),
        "metrics_preview": summarize_color_error(pred, target),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codec", default="outputs/hadamard_k6/codec.pt")
    parser.add_argument("--output", default="outputs/rgb_upsampler_k6")
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--lambda-max-abs", type=float, default=0.3)
    parser.add_argument("--lambda-color", type=float, default=0.05)
    parser.add_argument("--eval-count", type=int, default=240)
    parser.add_argument("--seed", type=int, default=260218741)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    model, codec = train(args)
    torch.save({"state_dict": model.state_dict(), "k": codec.k}, out / "upsampler.pt")
    payload = {
        "method": f"rgb_upsampler_k{codec.k}",
        "k": codec.k,
        "render_passes": codec.k // 3,
        "output_wavelengths": int(WAVELENGTHS.size),
        "experiments": {
            "rgb_upsampling_narrowband": _predict_rgb_asset_products(model, codec, "narrowband", args.eval_count)
        },
    }
    (out / "predictions.json").write_text(json.dumps(payload))
    print(json.dumps(payload["experiments"]["rgb_upsampling_narrowband"]["metrics_preview"], indent=2))


if __name__ == "__main__":
    main()
