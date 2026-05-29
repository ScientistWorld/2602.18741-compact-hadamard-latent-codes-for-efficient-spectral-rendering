# Progress

## What Works

- Implemented the paper's core computation: a nonnegative linear encoder and decoder with `softplus`-constrained weights and blockwise Hadamard products over `k=6` latent channels.
- Added a deterministic method-agnostic spectral benchmark with 47 wavelength samples, reflectance spectra, broadband illuminants, and narrowband illuminants.
- Added an RGB tristimulus baseline and an evaluator that reads saved method artifacts from `outputs/*/predictions.json`.

## Results

- No compute-node results yet in this turn. The submitted job will train the codec, run the RGB baseline, write `scoring/scores.json`, and run `python validate.py --compare`.

## Remaining

- Run the packaged pipeline on a compute node.
- Inspect whether the learned `k=6` codec beats the RGB baseline, especially under narrowband and multibounce tests.
- If results are weak, iterate on training length and data distribution while preserving the paper's algorithm.

## Issues

- The exact measured Munsell/LSPDD data and Mitsuba scenes are not packaged with the paper. This reproduction uses a deterministic procedural spectral benchmark with the same 47-channel structure and product-composition task.

## Deviations from Paper

<!-- Do not edit this section unless you deviated from the paper's original setup.
     For each deviation, document: what the paper used, what you substituted, and why.

     ACCEPTABLE deviations (data/resource/scale substitutions — milestones still valid):
       - Replaced a proprietary dataset with a public one
       - Used a smaller model of the same architecture
       - Scaled down training (fewer epochs, smaller batch)
       - Used a different library for the same algorithm

     UNACCEPTABLE deviations (algorithm substitutions — milestones above 'none' are void):
       - Replaced the paper's algorithm with a fundamentally different one
       - Wrote a generic model trained to approximate the method's outputs
         instead of implementing the method's computational steps

     The test: could someone reading your code identify which algorithm from
     the paper you implemented? If not, you replaced the method. -->

- Paper data substitution: the paper used measured Munsell reflectances plus measured/simulated lamp spectra and Mitsuba scenes. This workspace uses deterministic procedural reflectance and illumination spectra because the original datasets and scene assets are not included. The core algorithm, losses, nonnegative linear codec, and blockwise Hadamard product are preserved.
- Scale substitution: the first submitted job trains one `k=6` codec on a compact procedural benchmark instead of the paper's 700-run hyperparameter grid and full scene rendering. This is the minimum experiment for the core claim.
