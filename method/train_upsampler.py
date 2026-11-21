#!/usr/bin/env python3
"""Train the paper's RGB-to-latent upsampling MLP (Sec. 5) for a trained codec.

A single per-pixel MLP (3 -> 128 -> 128 -> k, SiLU) maps the linear-RGB value
of an asset to the frozen codec's latent code. Loss: latent MSE + 0.3 * mean
max-abs latent error + 0.05 * DeltaE76 of the decoded colours. AdamW (lr 2e-3,
weight decay 1e-5), batch 64, gradient clipping at 1.0, ReduceLROnPlateau
(factor 0.5, patience 200, min lr 1e-6), 4,500 epochs. As in the paper one
network serves both reflectances and illuminants. The result is appended to
``<codec-dir>/codec.json`` under ``upsampler``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.spectral_data import TRAIN_FILE, asset_rgb, load_library, xyz_matrix  # noqa: E402


class RGBToLatentUpsampler(nn.Module):
    def __init__(self, k: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.SiLU(), nn.Linear(hidden, k))

    def forward(self, rgb: torch.Tensor) -> torch.Tensor:
        return self.net(rgb)

    def export(self) -> dict:
        layers = [m for m in self.net if isinstance(m, nn.Linear)]
        acts = ["silu", "silu", "identity"]
        return {
            "layers": [
                {"weight": m.weight.detach().double().numpy().tolist(), "bias": m.bias.detach().double().numpy().tolist(), "activation": act}
                for m, act in zip(layers, acts)
            ]
        }


def _matrix(spec) -> np.ndarray:
    if isinstance(spec, dict) and "layers" in spec:
        if len(spec["layers"]) != 1 or spec["layers"][0].get("activation", "identity") not in ("identity", "linear"):
            raise ValueError("upsampler training supports linear codecs only")
        spec = spec["layers"][0]["weight"]
    return np.asarray(spec, dtype=np.float64)


def lab(xyz: torch.Tensor, white: torch.Tensor) -> torch.Tensor:
    t = xyz / white
    d = 6.0 / 29.0
    f = torch.where(t > d**3, t.clamp_min(d**3) ** (1.0 / 3.0), t / (3 * d * d) + 4.0 / 29.0)
    return torch.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], dim=1)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--codec-dir", default="outputs/hadamard_k6")
    p.add_argument("--epochs", type=int, default=4500)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=2e-3)
    p.add_argument("--weight-decay", type=float, default=1e-5)
    p.add_argument("--lambda-maxabs", type=float, default=0.3)
    p.add_argument("--lambda-color", type=float, default=0.05)
    p.add_argument("--hidden", type=int, default=128)
    p.add_argument("--seed", type=int, default=260218741)
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--train-file", default=str(TRAIN_FILE))
    args = p.parse_args(argv)

    torch.manual_seed(args.seed)
    torch.set_num_threads(args.threads)
    rng = np.random.default_rng(args.seed)
    codec_path = Path(args.codec_dir) / "codec.json"
    codec = json.loads(codec_path.read_text())
    enc_r = _matrix(codec.get("encoder_reflectance", codec.get("encoder")))
    enc_l = _matrix(codec.get("encoder_illuminant", codec.get("encoder")))
    dec = _matrix(codec["decoder"])
    k = enc_r.shape[0]

    lib = load_library(args.train_file)
    rgb = np.concatenate([asset_rgb(lib.reflectances, "reflectance", lib), asset_rgb(lib.illuminants, "illuminant", lib)])
    z = np.concatenate([np.clip(lib.reflectances @ enc_r.T, 0, None), np.clip(lib.illuminants @ enc_l.T, 0, None)])
    x_t = torch.as_tensor(rgb, dtype=torch.float32)
    z_t = torch.as_tensor(z, dtype=torch.float32)
    dec_t = torch.as_tensor(dec, dtype=torch.float32)
    xyz_t = torch.as_tensor(xyz_matrix(lib), dtype=torch.float32)
    white = torch.as_tensor(xyz_matrix(lib) @ lib.visible_mask, dtype=torch.float32)

    model = RGBToLatentUpsampler(k, args.hidden)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.5, patience=200, min_lr=1e-6)
    n = len(x_t)
    start = time.time()
    history = []
    for epoch in range(args.epochs):
        perm = torch.as_tensor(rng.permutation(n))
        total, count = 0.0, 0
        for s in range(0, n, args.batch_size):
            idx = perm[s:s + args.batch_size]
            z_pred = model(x_t[idx])
            z_gt = z_t[idx]
            diff = z_pred - z_gt
            latent = (diff**2).mean() + args.lambda_maxabs * diff.abs().max(dim=1).values.mean()
            lab_pred = lab((z_pred @ dec_t.T) @ xyz_t.T, white)
            lab_gt = lab((z_gt @ dec_t.T) @ xyz_t.T, white)
            color = torch.sqrt(((lab_pred - lab_gt) ** 2).sum(dim=1) + 1e-12).mean()
            loss = latent + args.lambda_color * color
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += float(loss) * len(idx)
            count += len(idx)
        epoch_loss = total / count
        sched.step(epoch_loss)
        if epoch % 100 == 0 or epoch == args.epochs - 1:
            history.append({"epoch": epoch, "loss": epoch_loss, "lr": opt.param_groups[0]["lr"]})

    codec["upsampler"] = model.export()
    codec_path.write_text(json.dumps(codec))
    log = {"config": vars(args), "seconds": time.time() - start, "history": history}
    (Path(args.codec_dir) / "upsampler_log.json").write_text(json.dumps(log, indent=2))
    print(json.dumps({"final_loss": history[-1], "seconds": log["seconds"]}, indent=2))


if __name__ == "__main__":
    main()
