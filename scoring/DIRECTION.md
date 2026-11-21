# Research Direction

## Research Problem

Make spectral rendering practical in RGB-oriented pipelines: represent
reflectance and illumination spectra compactly enough to render them through
at most two ordinary RGB passes, while the decoded result stays close to full
47-sample spectral rendering, including under spiky narrowband lights, after
several light-material interactions, in scenes where many light paths are
scaled and summed, and for assets that exist only as RGB values.

## Core Contribution

The contribution being studied is a compact, renderer-compatible spectral
representation whose behaviour under the renderer's operations (per-channel
multiplication, scaling, addition) approximates the true spectral algebra
well. Improvements should be of this kind.

## Approach Scope

You may change how the representation is constructed or learned, the
training objectives and data combinations drawn from the provided spectra,
separate treatment of reflectances and lights, the decoder (linear or not,
as long as it works from the rendered code alone), the RGB-to-code
upsamplers, and regularisation for physical plausibility or smoothness.

## Out of Bounds

- More than six code channels (two RGB passes), or full spectral rendering.
- Scene- or instance-specific regressors, lookup tables of evaluation
  answers, or anything that needs the held-out spectra.
- External spectra or re-downloaded source databases.
- Changing the evaluator's renderer, ground truth, exposure or metrics.
