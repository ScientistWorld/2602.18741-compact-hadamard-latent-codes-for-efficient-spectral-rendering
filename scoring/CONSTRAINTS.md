# Scientist Constraints

## Data

Use the provided spectral reflectance and illumination datasets and the fixed train/test split created for this benchmark. Do not add external measured spectra, synthetic spectra, rendered scenes, lights, or textures for training or tuning. The paper's claim is about a compact spectral representation learned and evaluated on this problem distribution; adding more spectra changes the benchmark rather than improving the method.

The held-out spectral test set and rendered evaluation scenes must not be used for training, model selection, threshold selection, or early stopping.

## Evaluation Budget

The main submission must include a compact setting with no more than two RGB-equivalent render passes per image. A higher-quality setting may be reported separately, but it cannot replace the compact setting for the main score. This prevents a trivial improvement from using full spectral rendering or simply increasing the number of wavelength samples.

## Ground Truth and Baselines

Use the benchmark's 47-channel spectral renderer output as ground truth. The RGB baseline must use the same scene, camera, materials, lights, resolution, sampler, and display conversion as the candidate evaluation. Do not change scene content or illumination to make the candidate method easier to score.

## Problem Formulation

The candidate must solve compact spectral rendering or compact spectral asset representation for rendering. It may not submit full 47-channel spectral rendering, scene-specific image regression, manual per-scene color correction, or lookup tables fitted directly to the evaluation images as the main method.

## Compliance Checklist

- [ ] Uses only the benchmark-provided training spectra and assets
- [ ] Does not train, tune, or select models on held-out test spectra or rendered test images
- [ ] Reports a main setting using no more than two RGB-equivalent render passes
- [ ] Uses 47-channel spectral renders as ground truth for all accuracy metrics
- [ ] Evaluates the RGB baseline under matched scene and rendering settings
- [ ] Does not replace the task with full spectral rendering or per-scene image regression
