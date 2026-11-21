# Evaluation Targets

All experiments are scored from `outputs/<method>/codec.json` by
`bash scripts/evaluate_train.sh` (public training spectra) and the hidden
`bash scripts/evaluate_test.sh` (held-out spectra). Lower is better for every
metric.

## Constraints (validity gates, enforced by the evaluator)

- **Render-pass budget**: the code has at most 6 channels (two RGB passes),
  measured from the submitted networks' shapes. Exceeding it fails the run.
- **Renderer compatibility**: codes are clamped to be nonnegative before
  rendering and only per-channel products, scaling and sums are applied; the
  decoder sees only the rendered code.
- **Physical outputs**: decoded spectra are clamped to be nonnegative;
  non-finite outputs fail the run.
- A failed run receives the worst value of every metric (CIE94 100, relative
  spectral error 2.0) in every experiment.

## spectral_product_broadband

Single interaction under broadband lights.
- **Primary metric**: mean_delta_e94
- **Also scored**: p95_delta_e94 (tail), spectral_nrmse (spectral fidelity)

## spectral_product_narrowband

Single interaction under spiky narrowband lights; the main stress case.
- **Primary metric**: mean_delta_e94
- **Also scored**: p95_delta_e94, spectral_nrmse

## multibounce_narrowband

Three successive interactions under narrowband lights.
- **Primary metric**: mean_delta_e94
- **Also scored**: p95_delta_e94, spectral_nrmse

## multibounce_proxy

The paper's selection protocol: mean CIE94 after one, two and three interactions.
- **Primary metric**: mean_delta_e94_3bounce
- **Also scored**: mean_delta_e94_1bounce, mean_delta_e94_2bounce
- **Paper**: 2.16 / 1.79 / 1.74 (different lamp database; see `scoring/reference.json`)

## rendered_scenes

Pixels summing 30 weighted paths of depth 1-8 from two lights over ten materials.
- **Primary metric**: mean_delta_e94
- **Also scored**: p95_delta_e94, spectral_nrmse

## rgb_upsampling

Assets supplied only as linear-sRGB values, broadband lights.
- **Primary metric**: mean_delta_e94
- **Also scored**: p95_delta_e94, spectral_nrmse
