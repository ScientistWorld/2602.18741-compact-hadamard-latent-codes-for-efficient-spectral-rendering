from __future__ import annotations

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class NonnegativeLinearHadamardCodec(nn.Module):
    """Paper's nonnegative linear encoder/decoder (Eq. 4-5) with blockwise products (Eq. 6).

    Both weight matrices are softplus(beta=10) reparameterisations of free
    parameters, so codes of nonnegative spectra and decoded spectra are
    nonnegative. One encoder is shared by reflectances and illuminants.
    """

    def __init__(self, n_wavelengths: int = 47, k: int = 6, beta: float = 10.0, init_scale: float = 0.05):
        super().__init__()
        if k % 3 != 0:
            raise ValueError("k must be divisible by 3 for RGB triplet packing")
        self.n_wavelengths = n_wavelengths
        self.k = k
        self.beta = beta
        self.raw_encoder = nn.Parameter(torch.randn(k, n_wavelengths) * init_scale)
        self.raw_decoder = nn.Parameter(torch.randn(n_wavelengths, k) * init_scale)

    def reset_from_bands(self, wavelengths: np.ndarray, visible_mask: np.ndarray, width_nm: float = 25.0) -> None:
        """Alternative initialisation: k evenly spaced smooth bands over 400-700 nm (data-agnostic)."""
        centers = np.linspace(400.0, 700.0, self.k + 2)[1:-1]
        bands = np.exp(-0.5 * ((wavelengths[None, :] - centers[:, None]) / width_nm) ** 2) * visible_mask[None, :]
        bands = torch.as_tensor(bands, dtype=self.raw_encoder.dtype)
        decoder = bands.T.clamp_min(1e-4)
        encoder = (bands / bands.sum(dim=1, keepdim=True)).clamp_min(1e-4)
        with torch.no_grad():
            self.raw_encoder.copy_(softplus_inverse(encoder, self.beta))
            self.raw_decoder.copy_(softplus_inverse(decoder, self.beta))

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

    @staticmethod
    def blockwise_product(z_left: torch.Tensor, z_right: torch.Tensor) -> torch.Tensor:
        """Blockwise Hadamard product over 3-channel (RGB-pass) blocks."""
        k = z_left.shape[-1]
        blocks = (z_left.reshape(-1, k // 3, 3) * z_right.reshape(-1, k // 3, 3))
        return blocks.reshape(z_left.shape)

    def product_code(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        return self.blockwise_product(self.encode(left), self.encode(right))

    def product_spectrum(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        return self.decode(self.product_code(left, right))

    def export(self) -> dict:
        """Matrices for codec.json (weight shapes are output x input)."""
        with torch.no_grad():
            return {
                "encoder": self.encoder_weight.double().cpu().numpy().tolist(),
                "decoder": self.decoder_weight.double().cpu().numpy().tolist(),
            }


def cosine_shaped_mse(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """L_e2e of the paper: MSE * (2 - cos)."""
    mse = F.mse_loss(pred, target)
    cos = F.cosine_similarity(pred, target, dim=-1, eps=1e-8).mean()
    return mse * (2.0 - cos)


def softplus_inverse(value: torch.Tensor, beta: float) -> torch.Tensor:
    x = (value * beta).clamp_min(1e-6)
    return torch.log(torch.expm1(x)) / beta
