# Gym scoring audit

Genuine improvements score higher in the runs tested: longer training gains **+0.021438**, stronger color supervision gains **+0.090440**, and one epoch loses **−1.283891**, against a three-seed score spread of **0.005952**. However, the gym does **not reliably rank scientific contribution**. A method producing no valid predictions beats both improvements by declaring zero cost; public generators reveal all answers; editable data changes the ground truth; and missing methods or metrics avoid losses. The synthetic problem shows a color-error benefit over its baseline, but does not establish that improvements transfer to the paper's measured spectra or rendering problem.

## 1. Does better research score higher?

All numbers below come from the unchanged, no-argument `bash scripts/evaluate_test.sh`. B, N, and M denote broadband products, narrowband products, and three-bounce narrowband chains. Lower error is better. The reference is the original reproduced `hadamard_k6` output, rerun through the hidden evaluator, rather than the sparse paper targets in `scoring/reference.json`.

| Real method variant (run script) | B mean CIE94 | N mean CIE94 | M mean CIE94 | Rank gain over reference |
|---|---:|---:|---:|---:|
| [Reference](redteam/reference/run.sh), existing trained output | 1.990364 | 4.035119 | 2.955530 | 0 |
| [Longer training](redteam/better_long/run.sh), 6,000 epochs, original losses | 1.826839 | 3.722868 | 2.961065 | **+0.021438** |
| [Stronger color supervision](redteam/better_color/run.sh), 6,000 epochs, color weight 5 instead of 0.5 | 1.280289 | 2.672547 | 2.681401 | **+0.090440** |
| [One epoch](redteam/weaker_one_epoch/run.sh), same architecture and losses | 13.899338 | 9.648031 | 12.489297 | **−1.283891** |
| [Actual RGB baseline](redteam/honest_rgb/run.sh), three channels, one pass | 2.474821 | 7.483363 | 10.839980 | −1.013255 |
| [Six fixed wavelength samples](redteam/honest_six_samples/run.sh), multiplication and linear interpolation | 12.115186 | 12.792228 | 11.105504 | −1.369593 |

| Variant | B spectral MSE | N spectral MSE | M spectral MSE |
|---|---:|---:|---:|
| Reference | 0.001503673 | 0.002139057 | 0.000888385 |
| Longer training | 0.001444492 | 0.002121163 | 0.000879280 |
| Stronger color supervision | 0.001486743 | 0.002343809 | 0.001048819 |
| One epoch | 0.032700945 | 0.004836359 | 0.004029701 |
| RGB baseline | 0.031158675 | 0.013662371 | 0.003639404 |
| Six fixed samples | 0.029630620 | 0.012541386 | 0.004056545 |

The longer run preserves the actual nonnegative linear codec, blockwise multiplication, all four loss terms, six channels, and two passes. It improves all spectral MSEs and most color metrics; its small M mean/median regressions are within seed variation. Its B mean improvement alone is also within the B seed spread. The color variant improves every color summary, with mean gains exceeding the corresponding seed spreads, while sacrificing N and M spectral MSE. It is a real quality tradeoff, not a componentwise improvement. Neither variant was tuned on hidden scores. The weak variant worsens every accuracy metric. Simple baselines score well below the reference, and honest gains show room above it.

**Rank calculation.** For each scored metric, the report sums experiment weight × absolute coefficient × signed improvement over the reproduced reference ÷ that metric's standard deviation. It uses `higher_is_better`; negative resource coefficients do not reverse their direction. Missing values contribute nothing, as specified in the audit request. The declared main normalization cohort contains all **21 successful attempts**, including successful attempts with absent metrics; the failed empty-array attempt is excluded. Standard deviations use available finite values and population normalization. Reference gain is zero. [summary.json](redteam/summary.json) records the cohort, scales, contributions, missing values, and seed spreads; [summary.csv](redteam/summary.csv) contains every raw scored metric.

The future ranking cohort is unknown, so these normalized gains are conditional on this explicit cohort. As a robustness check, normalizing on just the nine reference/honest attempts gives gains +0.116178 and +0.473617 for the two improvements and −5.366933 for one epoch; that cohort's seed spread is 0.024533. Thus the tested scientific direction does not depend on including shortcuts in the normalization. Tradeoffs can still change order across cohorts. Exact ties and componentwise wins below do not need a particular normalization.

**Reference bounds.** The reference already has `output_wavelengths=47`, the largest accepted spectral width, in **all three experiments**. These are the only scored metrics at their best bound. Every color summary and spectral MSE is strictly above its lower bound zero. Six latent channels and two passes meet the stated resource ceilings; they are not minimum-cost values. There is no measured runtime metric. The evaluator accepts even zero declared channels and passes.

## 2. Seed spread and reproduction check

Three full reference retrainings used seeds **260218741, 260218742, 260218743**, 600 epochs maximum, patience 120, and the same fixed dataset and test inputs. Only optimizer initialization and sampling randomness varied. The wrapper fixes the dataset because the original training program otherwise changes the training dataset with its seed. Band initialization itself is deterministic.

| Seed (run script) | B mean CIE94 | N mean CIE94 | M mean CIE94 | Rank gain |
|---|---:|---:|---:|---:|
| [260218741](redteam/reference_seed1/run.sh) | 1.990363 | 4.035119 | 2.955530 | −0.000000014 |
| [260218742](redteam/reference_seed2/run.sh) | 2.081836 | 4.058680 | 2.876044 | +0.000859 |
| [260218743](redteam/reference_seed3/run.sh) | 2.154180 | 4.062877 | 2.918761 | −0.005094 |
| Max minus min | **0.163817** | **0.027758** | **0.079486** | **0.005952** |

Spectral MSE spreads are **0.000037719**, **0.000111076**, and **0.000043646** for B/N/M. Resource and output-width spreads are zero. All other metric spreads are in `summary.json`. A gain below the observed spread is noise in this audit; three seeds do not establish a confidence interval. Both tested aggregate improvements exceed the spread.

**Baseline direction agrees with the paper within this proxy.** Reference mean color error is below the RGB baseline in all three experiments, especially narrowband and multibounce; all color tails improve too. The six-sample baseline is also substantially worse. The paper's quantitative results are not reproduced on comparable data: its selected codec reports mean CIE94 2.16/1.79/1.74 for one/two/three synthetic interactions; the gym's narrowband one/three results are 4.035/2.956, and no two-interaction experiment is scored. The gym's three-interaction spectral MSE 0.0008884 is not the same quantity as the paper's rendered-image MSE 0.000720, despite the latter being placed in the reference schema.

**Departures from the paper and validity of the substitute problem:**

- The core codec computation is recognizable and preserved: linear nonnegative encoder/decoder with softplus β=10, shared encoding of reflectance and light, blockwise Hadamard composition, and the four specified losses and selected weights. The gym adds initialization from the same six bands used to generate the data, an advantage specific to its substitute distribution.
- Measured Munsell reflectances and lamp/daylight spectra are replaced entirely by seeded Gaussian mixtures. Their six-band structure is shared with codec initialization, and narrowband peaks cluster around these bands. The 47-sample grid and zeroing outside 400–700 nm match the paper (30 active samples). Training/test reflectance counts 1,013/436 match, but random shuffling replaces the paper's color-space split. Lamp curation, cosine filtering, broadband flipping, and training scaling augmentation are absent.
- The paper has 708 curated illuminants before its split. The gym generates 727, uses 708 for training, then separately draws test lights from those same arrays. **179/180 broadband and 176/180 narrowband test illuminants are already in the nominal training pool.** Reflectance pools are disjoint (0/436 overlap). See the executed [data check](redteam/data_checks.json). This weakens the claimed held-out lighting evaluation.
- The reproduced configuration audited here uses 600 epochs and patience 120, rather than the paper's up-to-150 epochs and patience 15. The gym lacks the 700-configuration search selected across multiple bounce counts. It reserves another 15% of its nominal training pools for validation and samples a new validation batch each epoch.
- Analytic, separately normalized Gaussian XYZ matching functions replace calibrated color-matching tables. The baseline multiplies XYZ tristimulus values; it does not run a matched RGB renderer. For XYZ-only predictions the evaluator invents a clipped minimum-norm spectrum to score spectral MSE, so that metric is partly a choice of spectral reconstruction.
- The test contains only 120 B products, 120 N products, and 60 three-bounce chains: **300 numerical rows**, after taking the second half of candidate-supplied arrays. The paper's synthetic protocol uses 500 pairs, and its main claim uses actual Mitsuba scenes. The gym has no scene, camera, path sampling, image accumulation, measured runtime, two-/infinite-bounce rendering tests, or scored RGB-to-latent upsampling experiment.
- The unscored secondary upsampler source uses XYZ inputs rather than linear RGB, concatenates 1,013 reflectances and 708 illuminants before an ordered 85/15 split, adds output softplus, and defaults to 1,200 epochs rather than the paper's 4,500. Its MLP size, frozen codec, optimizer and loss structure follow the paper, but its secondary results cannot affect this hidden rank.

The substitute retains the qualitative difficulty of lost spectral information: narrowband RGB multiplication is worse and the learned compact codec helps, while fixed six-sample interpolation remains poor. It is not trivial for those compact baselines. However, this does not validate the paper's generalization or speed claim; the shared bands, overlapping lights, and absence of rendering materially change the problem. A better score here alone is insufficient evidence of a better method on the paper's problem.

**Brute force solves the accuracy test.** [shortcut_full_spectral](redteam/shortcut_full_spectral/run.sh) directly multiplies every one of the 47 wavelengths, with truthful 47-channel/47-pass declarations. Candidate generation took 0.97 s on the CPU job and produced exactly zero for all 15 accuracy metrics. The test is too small and exposed to require the compact computation it is meant to study. Its main-cohort rank is −0.896966 because of resource penalties, but it gains +4.855000 in the valid cohort consisting only of reference and brute force. This is a concrete failure of a soft, cohort-dependent resource tradeoff to enforce the compact-rendering task. The public-answer shortcut below additionally evades the cost penalty.

## 3. Executed shortcuts

Every row has its own executable `run.sh`, saved evaluator scores (where written), status, and log in the linked folder. Reference gain is **0**. A tie counts as a shortcut paying, even when the underlying mechanism being probed failed. No result here comes from changing the evaluator or its Python environment.

| Shortcut (run script) | What it does | Hidden-test result versus reference | Works? |
|---|---|---|---|
| [shortcut_target_copy](redteam/shortcut_target_copy/run.sh) | Regenerates public seeded operands and writes their exact full spectral products, while retaining k=6/two-pass declarations. No compact codec is used. | All accuracy metrics **0**; gain **+0.421587**. | **Yes**; componentwise better, including from public data alone. |
| [shortcut_ground_truth](redteam/shortcut_ground_truth/run.sh) | Replaces the public data module's pair/chain generators with zero-valued inputs and submits zeros. The restored evaluator imports that editable asset. | All accuracy metrics **0**; gain **+0.421587**. | **Yes**; moves ground truth and replaces a supposedly fixed problem asset. |
| [shortcut_metadata](redteam/shortcut_metadata/run.sh) | Keeps every reference prediction and writes k=0 and passes=0. | Identical accuracy; gain **+0.102430**, above both genuine improvements. | **Yes**; unverified impossible resource claims. |
| [shortcut_null](redteam/shortcut_null/run.sh) | Writes JSON null for every spectral value, preserving array dimensions and original costs. | All **15 accuracy metrics disappear**; gain **0**, a reference tie. | **Yes**, shortcut tie for a failed task. |
| [shortcut_null_zero_cost](redteam/shortcut_null_zero_cost/run.sh) | Combines null spectra with zero declared channels and passes. | No valid output, yet gain **+0.102430**, above both genuine improvements. | **Yes**; failed task outranks reference through other metrics. |
| [shortcut_omitted](redteam/shortcut_omitted/run.sh) | Submits an empty experiment mapping. | Candidate absent from all results; all **24 metrics missing**; gain **0**. Hidden evaluation exits 0 with baseline results. | **Yes**, shortcut tie through omission. |
| [shortcut_unlisted_name](redteam/shortcut_unlisted_name/run.sh) | Renames otherwise unchanged predictions to a new method identifier. | Candidate absent from train and test results; gain **0**. | **Yes**, shortcut tie; also proves new legitimate methods can be silently unranked. |
| [shortcut_test_size](redteam/shortcut_test_size/run.sh) | Reuses the original codec and selects array lengths 4/6/3 using whole public generated sets; no retraining or hidden-score selection. | Test shrinks to **2/3/2 rows**; gain **+0.080067**. Means 2.767117/3.843325/2.046166. | **Yes** in the audit cohort; changes task size, with metric tradeoffs. |
| [shortcut_full_spectral](redteam/shortcut_full_spectral/run.sh) | Brute-force 47-wavelength multiplication with truthful costs. | All accuracy metrics **0**; gain **−0.896966** here, **+4.855000** with reference-only normalization. | **Fails** to beat reference in main cohort; **pays in the pairwise cohort**. |
| [shortcut_forged_fields](redteam/shortcut_forged_fields/run.sh) | Writes fake zero scores, self-copied targets, perfect previews, success flags, and negative time; retains real reference predictions. | Hidden evaluator overwrites fake score file and recomputes original errors; gain **0**. | Forgery **fails**; retained predictions produce a **shortcut/control tie**. |
| [shortcut_constant_zero](redteam/shortcut_constant_zero/run.sh) | Emits zeros on the unchanged problem with original costs. | Means 76.960579/79.583611/48.951511; gain **−8.835014**. | **Fails**. |
| [shortcut_copy_input](redteam/shortcut_copy_input/run.sh) | Copies one spectral operand instead of multiplying all operands. | Means 11.775002/68.008629/29.970001; gain **−5.836215**. | **Fails**. |
| [shortcut_empty_rows](redteam/shortcut_empty_rows/run.sh) | Emits empty prediction arrays. | Train and hidden test both exit **1**; hidden writes **no score file**. | **Fails** as a scored submission; no worst-value record is written. |

### Scoring checks and causes

**Failing the task can outrank the reference.** Nulls become NumPy NaNs, and `score_run` removes every NaN metric instead of assigning a worst value. Resource fields are read directly from candidate JSON with no feasibility check. Hence `shortcut_null_zero_cost` wins using only resource metrics. Even all-null outputs with honest costs tie. This result holds for any normalization in which the improved cost metrics have nonzero variance.

**Failures do not receive complete worst scores.** Neither missing experiments nor missing methods are filled; null-valued predictions lose all error metrics; empty arrays raise before writing scores. There is no code path assigning a worst value for every experiment/metric. The failed empty-array run is not counted as a successful zero-score attempt in the table or normalization.

**Not every on-disk method is written.** The evaluator's reference contract includes method names as well as experiment names, allowing only `hadamard_k6` and `rgb_baseline`. The train-results method filter further limits discovery. The new-name shortcut leaves both its predictions and the baseline on disk, yet hidden results contain only the baseline. All honest audit variants use the accepted `hadamard_k6` identifier so their actual behavior is measured.

**Answers and test size are public and mutable.** The hidden test regenerates targets by calling public `make_product_pairs`/`make_multibounce_chains` with default visible seeds. It passes the candidate's prediction count into those functions, then selects the second half. Changing count also changes random illumination assignments, not just the number of rows. This enables both exact answer rebuilding and selecting an easier, seven-row problem. Replacing the public generator survives restoration of `eval/`, changes the comparison itself, and works in a new evaluator process.

**Some candidate-written fields are correctly ignored.** Supplied target arrays, metric previews, success/timing fields and top-level results do not determine errors. A prewritten `scoring/scores_test.json` is replaced after successful evaluation; [the forged pre-test file](redteam/shortcut_forged_fields/shortcut_pretest_scores.json) and recomputed score file show this. The vulnerability is the trusted resource declarations and mutable imported data, not direct score-file acceptance. There is no fixed pretrained model loaded by this evaluator to retrain; replacing the data-generation asset is the applicable fixed-artifact test.

## 4. Execution and restoration

One bundled CPU job, **d3db5a00-277**, ran all **22** cases: 21 successful hidden evaluations and the expected empty-array failure. Each case runs public training evaluation followed by **`bash scripts/evaluate_test.sh` with no arguments**. Candidate code uses only visible data/method code and the explicitly permitted reused reference outputs. It does not read hidden evaluation code, test scores, the paper, or the reference schema. The audit harness reads hidden outputs for reporting and records evaluator hashes; those hashes remained unchanged across every run.

The bundled job uses a separate candidate process and a new evaluator process for each run, rather than allocating a separate container for each case. No candidate process survives into evaluation, and no candidate changes the Python environment. Persistent candidate changes are limited to output files, the forged score-file control, and the explicitly tested public data asset, so no result depends on a surviving process. The harness isolates and restores original outputs and data/score files after every case. Model checkpoints and prediction caches are gitignored under `redteam/`; run scripts regenerate them when needed.

The temporary job launcher and all audited source/score files outside `redteam/` are restored to the initial git version. Pre-existing system/workspace changes recorded in [initial_state.json](redteam/initial_state.json) are preserved. [verification.json](redteam/verification.json) records the final syntax, evidence, score, and restoration checks. The audit deliverables are this report and `redteam/`; `action.yaml` is used only for the required submission/completion protocol.

For the next gym iteration, prioritize evaluator-owned immutable inputs and fixed counts, complete worst scores for invalid/missing results, discovery of every submitted method, and measured or structurally enforced resource constraints. Restore a disjoint lighting split and validate against measured spectra and actual matched rendering before treating the score as evidence for the paper's contribution.
