# Research Direction

## Research Problem

This benchmark asks how to make spectral rendering practical in RGB-oriented rendering pipelines. The goal is not to improve a particular scene, but to represent wavelength-dependent reflectance and illumination compactly enough that rendered images stay close to full spectral ground truth while using only a small number of RGB-equivalent passes.

## Core Contribution

The paper's contribution is a compact renderer-compatible spectral representation that preserves the operations needed during rendering well enough to approximate full spectral results. Future work should improve this same class of contribution: compact spectral representations and their composition behavior under rendering-like operations.

## Approach Scope

Scientists may change the representation, training objective, basis construction, regularization, RGB-asset conversion strategy, or compact decoding procedure. They may also improve how compact representations are composed during rendering, provided the main result remains a compact spectral rendering method evaluated under the same two-pass budget.

## Out of Bounds

- Replacing the benchmark with full spectral rendering as the main method.
- Using a scene-specific neural renderer that directly maps camera rays or pixels to final RGB images.
- Optimizing per-scene color correction or lookup tables against the evaluation images.
- Improving scores only by adding external spectra, external scenes, or more render passes.
- Changing the problem to a general RGB-to-spectrum recovery benchmark without rendering evaluation.
