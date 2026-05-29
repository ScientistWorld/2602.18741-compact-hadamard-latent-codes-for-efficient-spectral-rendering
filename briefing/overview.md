# Overview

- **Paper ID:** 2602.18741
- **Title:** Compact Hadamard Latent Codes for Efficient Spectral Rendering
- **Domain:** Computer Graphics / Spectral Rendering
- **TL;DR:** The paper learns compact spectral codes that can be rendered as a few RGB passes while approximating full spectral rendering much more accurately than ordinary RGB rendering.

## Short Summary

Full spectral rendering is accurate under wavelength-dependent materials and illumination, but it is much more expensive than RGB rendering because it evaluates many wavelength samples. This paper proposes a compact latent spectral representation designed to support rendering-style composition, allowing spectral assets to be rendered through standard RGB infrastructure and decoded back to spectra or display colors. The reported main configuration uses six latent channels, rendered as two RGB passes, and is evaluated against 47-channel spectral rendering ground truth. The paper also studies RGB-asset conversion, narrowband illumination stress cases, and stability across repeated light-material interactions.

## Key Results

- The `k=6` setting uses two RGB render passes instead of 47 spectral samples, reported as roughly a `23x` render-pass reduction.
- In a synthetic multi-bounce test used for model selection, the selected configuration reports mean CIE94 errors of `2.16`, `1.79`, and `1.74` for one, two, and three bounces.
- The paper claims lower color error than standard RGB rendering, especially under narrowband illumination, while remaining visually close to 47-channel spectral ground truth in several rendered scenes.
