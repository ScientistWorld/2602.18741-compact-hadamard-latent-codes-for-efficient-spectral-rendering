"""Honest codec variants; keep the benchmark data fixed across random seeds."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from data.spectral_common import make_dataset
from method import train_codec as training


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--epochs", type=int, default=600)
    parser.add_argument("--seed", type=int, default=260218741)
    parser.add_argument("--patience", type=int, default=120)
    parser.add_argument("--color-weight", type=float, default=0.5)
    args = parser.parse_args()
    torch.set_num_threads(1)
    fixed_dataset = make_dataset()
    training.make_dataset = lambda seed=None: fixed_dataset
    config = argparse.Namespace(
        epochs=args.epochs, seed=args.seed, early_stop=args.patience,
        k=6, device="cpu", batch_size=128, lr=1e-3, band_init=True,
        lambda_e2e=0.5, lambda_rec=0.75, lambda_code=1.0,
        lambda_col=args.color_weight,
    )
    codec = training.train(config)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": codec.state_dict(), "k": 6}, out / "codec.pt")
    payload = {
        "method": "hadamard_k6", "k": 6, "render_passes": 2,
        "experiments": {
            "spectral_product_broadband": training._predict_product(codec, "broadband", 240),
            "spectral_product_narrowband": training._predict_product(codec, "narrowband", 240),
            "multibounce_narrowband": training._predict_multibounce(codec, "narrowband", 120),
        },
    }
    (out / "predictions.json").write_text(json.dumps(payload))
    (out / "training_config.json").write_text(json.dumps(vars(config), indent=2))


if __name__ == "__main__":
    main()
