# Scientist Constraints

## Data

Train, tune and select only on the spectra in `data/spectra_train.json`.
Do not add external spectra of any kind: no other reflectance or light
databases, no re-download of the public Munsell, CIE or lamp sources these
spectra were built from, and no extra synthetic spectra. The held-out test
spectra are drawn from the same public sources, so bringing them in is
training on the test set. Generating new training *combinations* of the
provided spectra (products, chains, mixtures, scaled lights) is allowed.

The held-out spectra, the hidden evaluator and its instances must not be read
or used for training, model selection or early stopping.

## Evaluation Budget

The submitted code has at most six channels, i.e. two RGB-equivalent render
passes. The evaluator measures this from the submitted networks and fails
any submission above it; a wider "higher quality" setting cannot be scored.

## Ground Truth and Baselines

Ground truth is 47-sample spectral rendering on the evaluator's instances.
The RGB baseline, the exposure rules, the colour science and all instances
are fixed by `eval/` and are not part of a submission.

## Problem Formulation

A submission is a compact spectral representation: encoders for spectral
assets, a decoder for rendered codes and, for legacy assets, RGB upsamplers.
Rendering between them is done by the evaluator with per-channel products,
scaling and sums only. Do not try to identify specific assets or scenes,
memorise answers, or encode information that only works for the evaluator's
particular instances.

## Compliance Checklist

- [ ] Uses only `data/spectra_train.json` for training and selection
- [ ] No external or re-downloaded spectra, no use of held-out spectra
- [ ] Code width at most six channels (two RGB passes)
- [ ] Encoders act on one asset at a time; the decoder sees only the rendered code
- [ ] Submission is `outputs/<method>/codec.json` in the documented format
