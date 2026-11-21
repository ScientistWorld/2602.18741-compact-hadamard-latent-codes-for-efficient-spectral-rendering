#!/usr/bin/env python3
"""Train the paper's nonnegative linear Hadamard codec (Sec. 4) and export codec.json.

Defaults follow the paper: k = 6, softplus(beta = 10) nonnegative linear
encoder/decoder shared by reflectances and illuminants, blockwise Hadamard
products, loss weights lambda_e2e = 0.5, lambda_rec = 0.75, lambda_code = 1.0,
lambda_col = 0.5 (the selected configuration), Adam with lr 1e-3, batch 128,
up to 150 epochs with early stopping (patience 15) on a validation subset drawn
once at random from the training spectra (shared by all runs), and scaling
augmentation of the lights.
An epoch is one pass over all training reflectance-illuminant pairs. Like the
paper, which reports the codec selected from many trained runs, the
configuration is trained from 5 independent restarts and the restart with the
lowest validation loss is kept.

Optional flags (off by default) implement variants that go beyond the paper.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.spectral_data import TRAIN_FILE, load_library, xyz_matrix  # noqa: E402
from method.hadamard_codec import NonnegativeLinearHadamardCodec, cosine_shaped_mse  # noqa: E402


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--output", default="outputs/hadamard_k6")
    p.add_argument("--k", type=int, default=6)
    p.add_argument("--epochs", type=int, default=150)
    p.add_argument("--patience", type=int, default=15, help="early-stopping patience in epochs (0 disables)")
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=260218741, help="optimisation seed (initialisation, pair order, augmentation)")
    p.add_argument("--split-seed", type=int, default=20260221, help="seed of the one-off validation draw, shared by all runs")
    p.add_argument("--restarts", type=int, default=5, help="independent restarts; the lowest validation loss is kept")
    p.add_argument("--lambda-e2e", type=float, default=0.5)
    p.add_argument("--lambda-rec", type=float, default=0.75)
    p.add_argument("--lambda-code", type=float, default=1.0)
    p.add_argument("--lambda-col", type=float, default=0.5)
    p.add_argument("--val-fraction", type=float, default=0.15)
    p.add_argument("--scale-aug", type=float, nargs=2, default=[0.5, 1.5], metavar=("LOW", "HIGH"))
    p.add_argument("--init", choices=["random", "bands"], default="random")
    p.add_argument("--max-steps-per-epoch", type=int, default=0, help="0 = full pass over all pairs")
    # Variants beyond the paper (all off by default).
    p.add_argument("--lambda-chain", type=float, default=0.0, help="weight of extra 2- and 3-bounce chain losses")
    p.add_argument("--exposure-normalize", action="store_true", help="normalise product losses by each light's exposure")
    p.add_argument("--train-file", default=str(TRAIN_FILE))
    p.add_argument("--extra-reflectances-from", default=None, help="audit only: add Munsell reflectances from another library file")
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--method-name", default=None)
    return p.parse_args(argv)


class Trainer:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        torch.manual_seed(args.seed)
        torch.set_num_threads(args.threads)
        self.rng = np.random.default_rng(args.seed)
        lib = load_library(args.train_file)
        refl = lib.reflectances
        if args.extra_reflectances_from:
            extra = load_library(args.extra_reflectances_from)
            keep = [i for i, s in enumerate(extra.reflectance_source) if s == "munsell"]
            refl = np.concatenate([refl, extra.reflectances[keep]])
        illum = lib.illuminants
        # The validation subset is drawn once from the training spectra and is the
        # same for every run ("all runs used the same data"); only the optimisation
        # randomness depends on --seed.
        split_rng = np.random.default_rng(args.split_seed)
        r_perm = split_rng.permutation(len(refl))
        l_perm = split_rng.permutation(len(illum))
        n_rv = int(round(args.val_fraction * len(refl)))
        n_lv = int(round(args.val_fraction * len(illum)))
        as_t = lambda x: torch.as_tensor(np.asarray(x), dtype=torch.float32)  # noqa: E731
        self.r_val, self.r_tr = as_t(refl[r_perm[:n_rv]]), as_t(refl[r_perm[n_rv:]])
        self.l_val, self.l_tr = as_t(illum[l_perm[:n_lv]]), as_t(illum[l_perm[n_lv:]])
        self.cmf = as_t(lib.cmf)  # raw CIE colour-matching functions (T_cmf)
        xyz = xyz_matrix(lib)
        self.xyz = as_t(xyz)
        self.white = as_t(xyz @ lib.visible_mask)
        self.codec = NonnegativeLinearHadamardCodec(n_wavelengths=refl.shape[1], k=args.k)
        if args.init == "bands":
            self.codec.reset_from_bands(lib.wavelengths, lib.visible_mask)
        self.opt = torch.optim.Adam(self.codec.parameters(), lr=args.lr)
        vr, vl = np.meshgrid(np.arange(n_rv), np.arange(n_lv), indexing="ij")
        self.val_r = vr.ravel()
        self.val_l = vl.ravel()
        self.val_chain = self.rng.integers(n_rv, size=(len(self.val_r), 2))

    def exposure(self, light: torch.Tensor) -> torch.Tensor:
        rel = (light @ self.xyz.T) / self.white
        return 1.0 / rel.max(dim=-1, keepdim=True).values.clamp_min(1e-8)

    def loss(self, r: torch.Tensor, l: torch.Tensor, chain: tuple[torch.Tensor, torch.Tensor] | None):
        a, codec = self.args, self.codec
        target = r * l
        z_r, z_l = codec.encode(r), codec.encode(l)
        z_prod = codec.blockwise_product(z_r, z_l)
        pred = codec.decode(z_prod)
        e = self.exposure(l) if a.exposure_normalize else torch.ones_like(l[:, :1])
        loss_e2e = cosine_shaped_mse(pred * e, target * e)
        loss_rec = F.mse_loss(codec(r), r) + F.mse_loss(codec(l), l)
        loss_code = F.mse_loss(z_prod, codec.encode(target))
        loss_col = F.mse_loss((pred * e) @ self.cmf.T, (target * e) @ self.cmf.T)
        total = a.lambda_e2e * loss_e2e + a.lambda_rec * loss_rec + a.lambda_code * loss_code + a.lambda_col * loss_col
        if a.lambda_chain > 0 and chain is not None:
            z, t, chain_loss = z_prod, target, 0.0
            for extra in chain:
                z = codec.blockwise_product(z, codec.encode(extra))
                t = t * extra
                p = codec.decode(z)
                chain_loss = chain_loss + cosine_shaped_mse(p * e, t * e) + F.mse_loss((p * e) @ self.cmf.T, (t * e) @ self.cmf.T)
            total = total + a.lambda_chain * chain_loss
        return total

    def validation_loss(self) -> float:
        with torch.no_grad():
            r = self.r_val[self.val_r]
            l = self.l_val[self.val_l]
            chain = (self.r_val[self.val_chain[:, 0]], self.r_val[self.val_chain[:, 1]])
            return float(self.loss(r, l, chain))

    def run(self) -> dict:
        a = self.args
        n_r, n_l = len(self.r_tr), len(self.l_tr)
        n_pairs = n_r * n_l
        steps = n_pairs // a.batch_size
        if a.max_steps_per_epoch:
            steps = min(steps, a.max_steps_per_epoch)
        lo, hi = a.scale_aug
        best = float("inf")
        best_state = {k: v.detach().clone() for k, v in self.codec.state_dict().items()}
        wait = 0
        history = []
        start = time.time()
        epochs_run = 0
        for epoch in range(a.epochs):
            perm = torch.as_tensor(self.rng.permutation(n_pairs))
            self.codec.train()
            for s in range(steps):
                idx = perm[s * a.batch_size:(s + 1) * a.batch_size]
                r = self.r_tr[idx // n_l]
                l = self.l_tr[idx % n_l] * (lo + (hi - lo) * torch.rand(len(idx), 1))
                chain = None
                if a.lambda_chain > 0:
                    extra = torch.randint(n_r, (2, len(idx)))
                    chain = (self.r_tr[extra[0]], self.r_tr[extra[1]])
                loss = self.loss(r, l, chain)
                self.opt.zero_grad(set_to_none=True)
                loss.backward()
                self.opt.step()
            epochs_run = epoch + 1
            self.codec.eval()
            value = self.validation_loss()
            history.append(value)
            if value < best - 1e-12:
                best, wait = value, 0
                best_state = {k: v.detach().clone() for k, v in self.codec.state_dict().items()}
            else:
                wait += 1
            if a.patience and wait >= a.patience:
                break
        self.codec.load_state_dict(best_state)
        return {
            "epochs_run": epochs_run,
            "steps_per_epoch": steps,
            "best_validation_loss": best,
            "validation_history": history,
            "train_pairs": n_pairs,
            "seconds": time.time() - start,
        }


def main(argv=None) -> None:
    args = parse_args(argv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    # Independent restarts (seeds seed .. seed+R-1) of the same configuration on
    # the same data; keep the one with the lowest validation loss. Selection
    # uses the training spectra only.
    best = None
    restarts = []
    for i in range(args.restarts):
        run_args = argparse.Namespace(**{**vars(args), "seed": args.seed + i})
        trainer = Trainer(run_args)
        log = trainer.run()
        restarts.append({k: log[k] for k in ("best_validation_loss", "epochs_run", "seconds")} | {"seed": run_args.seed})
        if best is None or log["best_validation_loss"] < best[1]["best_validation_loss"]:
            best = (trainer, log, run_args.seed)
    trainer, log, seed = best
    torch.save({"state_dict": trainer.codec.state_dict(), "k": args.k}, out / "codec.pt")
    codec = {"method": args.method_name or out.name, "k": args.k}
    codec.update(trainer.codec.export())
    codec_path = out / "codec.json"
    if codec_path.exists():  # a new codec invalidates any upsampler trained for the old one
        codec_path.unlink()
    codec_path.write_text(json.dumps(codec))
    summary = {"config": vars(args), "selected_seed": seed, "restarts": restarts, **log}
    (out / "train_log.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("validation_history", "config")}, indent=2))


if __name__ == "__main__":
    main()
