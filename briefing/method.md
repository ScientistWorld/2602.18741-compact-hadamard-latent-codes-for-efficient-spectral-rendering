# Paper's Method

## Key Contribution

The paper introduces Hadamard spectral codes: compact nonnegative latent vectors for spectra that are meant to be manipulated with the same scaling, addition, and elementwise multiplication operations used in rendering. The main practical point is that a `k`-channel code can be split into RGB triplets and rendered through an unmodified RGB renderer in `k / 3` passes.

## Approach

The codec is a linear encoder-decoder with nonnegative weights. Linearity makes scaling and addition exact in the latent space, while training losses encourage the elementwise product of two latent codes to decode like the spectral product of the original spectra. The paper uses a blockwise product over three-channel groups so that each group corresponds to one RGB render pass.

Training uses reflectance and illumination spectra resampled to 47 wavelength samples. The loss combines end-to-end spectral product reconstruction, direct spectrum reconstruction, latent product consistency, and color-aware supervision through CIE color matching functions. The paper selects hyperparameters using a synthetic multi-bounce proxy that tests repeated reflectance-radiance products.

For legacy RGB content, the paper adds a small per-pixel MLP that maps RGB colors to the learned latent code space. The pretrained spectral decoder is then used to recover spectra or renderable latent assets.

## Main Claims

- **Primary:** A six-channel code rendered as two RGB passes can approximate 47-channel spectral rendering substantially better than standard RGB rendering while reducing render-pass count by about `23x`.
- **Primary constraint:** The representation must remain renderer-friendly: compact, nonnegative for physical spectra, and usable through standard RGB render passes.
- **Secondary:** The approach remains stable across repeated light-material interactions rather than accumulating runaway color error.
- **Secondary:** RGB-only assets can be mapped into the latent space and rendered with better spectral color behavior than ordinary RGB rendering.
