from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class NonnegativeLinearHadamardCodec(nn.Module):
    """Paper's nonnegative linear encoder/decoder with blockwise products."""

    def __init__(self, n_wavelengths: int = 47, k: int = 6, beta: float = 10.0):
        super().__init__()
        if k % 3 != 0:
            raise ValueError("k must be divisible by 3 for RGB triplet packing")
        self.n_wavelengths = n_wavelengths
        self.k = k
        self.beta = beta
        self.raw_encoder = nn.Parameter(torch.randn(k, n_wavelengths) * 0.04 - 0.25)
        self.raw_decoder = nn.Parameter(torch.randn(n_wavelengths, k) * 0.04 - 0.25)

    @property
    def encoder_weight(self) -> torch.Tensor:
        return F.softplus(self.raw_encoder, beta=self.beta)

    @property
    def decoder_weight(self) -> torch.Tensor:
        return F.softplus(self.raw_decoder, beta=self.beta)

    def encode(self, spectra: torch.Tensor) -> torch.Tensor:
        return spectra @ self.encoder_weight.T

    def decode(self, codes: torch.Tensor) -> torch.Tensor:
        return codes @ self.decoder_weight.T

    def forward(self, spectra: torch.Tensor) -> torch.Tensor:
        return self.decode(self.encode(spectra))

    def product_code(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        z_left = self.encode(left).view(-1, self.k // 3, 3)
        z_right = self.encode(right).view(-1, self.k // 3, 3)
        return (z_left * z_right).view(-1, self.k)

    def product_spectrum(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        return self.decode(self.product_code(left, right))


def cosine_shaped_mse(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    mse = F.mse_loss(pred, target)
    cos = F.cosine_similarity(pred, target, dim=-1, eps=1e-8).mean()
    return mse * (2.0 - cos)
