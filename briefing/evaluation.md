# Evaluation

## Metrics

- **Color error:** Report perceptual color difference against 47-channel spectral ground truth after converting rendered spectra to CIE XYZ/Lab. Use CIE94 for the multi-bounce spectral-chain test; lower is better.
- **Image error:** Report per-pixel MSE between the candidate render and spectral ground truth for rendered scenes; lower is better.
- **RGB baseline gap:** Report the same color or image errors for ordinary RGB rendering and require the candidate to improve over it, especially under narrowband illumination.
- **Efficiency:** Report the number of RGB-equivalent render passes or wavelength samples required per image. Lower is better, provided accuracy constraints are still met.
- **Stability:** Report how error changes across one, two, three, and unbounded or high-depth light transport settings. Stable or decreasing error is better than runaway accumulation.

## Baselines and Targets

- **Ground truth:** 47-channel spectral rendering over the paper's wavelength grid.
- **Primary baseline:** Standard RGB rendering of the same scene, materials, lights, camera, resolution, and sampler settings.
- **Paper target:** The main reported setting uses six compact channels rendered as two RGB passes. The paper reports roughly a `23x` render-pass reduction versus 47-channel spectral rendering.
- **Multi-bounce target:** In the paper's synthetic multi-bounce selection protocol, the selected configuration reports mean CIE94 errors of `2.16`, `1.79`, and `1.74` for one, two, and three bounces.
- **Narrowband stress reference:** The paper's supplemental narrowband multi-bounce image test reports MSE values around `8.17e-4`, `7.88e-4`, `7.20e-4`, and `7.11e-4` from one bounce through unbounded depth.

## Evaluation Protocol

Evaluate all methods on held-out reflectance and illumination spectra, not on spectra used for fitting or tuning. Use the same spectral-to-XYZ conversion, white point, tone mapping, resolution, camera, light spectra, and sample count for every method in a scene comparison. For RGB-asset tests, evaluate ordinary RGB rendering and the candidate RGB-to-spectral or RGB-to-rendering pipeline against the same spectral ground truth scene.

Report separate results for broadband illumination, narrowband illumination, and repeated-interaction tests. For the multi-bounce spectral-chain test, sample held-out reflectance-light pairs, repeatedly compose additional held-out reflectances for one to three bounces, and compare the resulting colors to the full spectral chain. For rendered scenes, include the main practical efficiency setting and any higher-quality reference setting separately.
