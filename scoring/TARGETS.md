# Evaluation Targets

## Primary: spectral_color_accuracy

Tests whether rendered images match full spectral ground truth more closely than ordinary RGB rendering across the main scene and illumination settings.
- **Metric**: mean_delta_e94 or image_mse (lower is better)
- **How to run**: Render the fixed evaluation scenes with the candidate method, full spectral ground truth, and RGB baseline; compare candidate and baseline errors against the spectral ground truth.

## Constraint: render_pass_efficiency

Tests whether accuracy is achieved with a compact RGB-renderer-compatible budget rather than by falling back to many spectral samples.
- **Metric**: render_passes or spectral_sample_equivalent_passes (lower is better, subject to accuracy targets)
- **How to run**: Count the number of RGB-equivalent render passes or wavelength-sample passes required by the candidate method for the same output image.

## Constraint: multibounce_stability

Tests whether error remains controlled when spectral quantities undergo repeated light-material interactions.
- **Metric**: bounce_error_growth (lower is better)
- **How to run**: Evaluate one-, two-, and three-bounce held-out spectral chains and compare each output to the full spectral chain; summarize both absolute error and growth between bounces.

## Constraint: narrowband_robustness

Tests whether the method remains accurate under spiky or narrowband illumination where RGB rendering is known to fail.
- **Metric**: narrowband_mean_mse or narrowband_delta_e94 (lower is better)
- **How to run**: Render the fixed narrowband-light scene and compare against 47-channel spectral ground truth using the same camera, materials, and sampling settings as other methods.

## Secondary: rgb_asset_compatibility

Tests whether scenes that start from RGB textures or colors can still benefit from the spectral evaluation pipeline.
- **Metric**: rgb_asset_delta_e or rgb_asset_image_mse (lower is better)
- **How to run**: Evaluate the fixed RGB-asset scenes against their spectral ground truth counterparts and compare to ordinary RGB rendering.
