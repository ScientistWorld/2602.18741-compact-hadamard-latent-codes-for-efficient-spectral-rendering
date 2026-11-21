# Train/Test Evaluation Design Notes

## Checks Performed

- Compared `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh`: train calls `eval/train/` and writes `scoring/scores_train.json`; test calls `eval/test/` and writes `scoring/scores_test.json`.
- Checked for hardcoded method defaults in the train/test scripts; both forward explicit run arguments or enumerate `outputs/*/predictions.json` through the evaluator.
- Checked for train/test cross-imports; the slice evaluators are duplicated and do not import from each other.
- Checked for paper-agreement metric names; no active metric is a deviation-from-paper or fit-to-published-results metric.
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` are absent.
- Ran `bash -n` on both train/test shell scripts.

## Changes Made

- Added tail-risk color metrics to both train and held-out test slices:
  - `p95_delta_e94`
  - `worst_decile_delta_e94`
- These metrics make the split harder to game by optimizing only average color error while leaving a hard subset with large artifacts.
- Changed train/test evaluators to infer `output_wavelengths` from the actual prediction tensor shape instead of trusting the JSON payload field.
- Added required `description` fields for every active metric in `scoring/reference.json`.
- Adjusted several metric coefficients to give tail errors meaningful weight, especially on narrowband and multibounce stress cases.

## Runtime Concerns For The Next Iteration

- `render_passes` and `latent_channels` are still declared by the candidate artifact because the evaluator cannot infer them from prediction JSON alone. A dishonest method can underreport these constraints unless a later runner adds artifact-level validation or a stricter output contract.
- The held-out test slice currently rescoring the second half of each prediction artifact is lightweight and method-agnostic, but the underlying procedural data generator is visible in `data/`. This still detects narrow train-slice overfitting, but it is less resistant than a fully hidden challenge set.
- Existing `scoring/scores.json` was not regenerated in this design-only iteration, so it does not contain the newly added tail metrics. The runner iteration should regenerate official scores through the normal evaluation path if those metrics are expected in current score artifacts.

## Superseded (iteration 11)

The runtime concerns above are resolved: methods now submit codecs that the hidden evaluator runs on held-out spectra stored only in eval/test/, the pass budget is measured from the submitted networks, and the old prediction-file evaluators were removed. See HARDENING.md.
