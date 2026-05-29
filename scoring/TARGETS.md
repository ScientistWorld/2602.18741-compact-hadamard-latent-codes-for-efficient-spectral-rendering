# Evaluation Targets

## spectral_product_broadband

Tests the central benefit claim on single material-light products under smooth broadband illumination.
- **Primary metric**: mean_delta_e94 (lower is better)
- **Constraint metrics**: render_passes and spectral_samples (lower is better)
- **How to run**: `bash scripts/evaluate.sh` after generating `outputs/hadamard_k6/predictions.json` and `outputs/rgb_baseline/predictions.json`.

## spectral_product_narrowband

Tests the difficult illumination setting emphasized by the paper, where RGB rendering has large color shifts.
- **Primary metric**: mean_delta_e94 (lower is better)
- **Constraint metrics**: render_passes and spectral_samples (lower is better)
- **How to run**: `bash scripts/evaluate.sh` after generating the method and baseline artifacts.

## multibounce_narrowband

Tests whether repeated multiplicative light-material interactions remain stable under narrowband illumination.
- **Primary metric**: spectral_mse (lower is better)
- **Benefit metric**: mean_delta_e94 (lower is better)
- **Constraint metrics**: render_passes and spectral_samples (lower is better)
- **How to run**: `bash scripts/evaluate.sh` after generating the method and baseline artifacts.
