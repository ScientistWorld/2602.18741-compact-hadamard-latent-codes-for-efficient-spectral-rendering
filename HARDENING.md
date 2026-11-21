# Hardening report

## Summary

The red-team audit found that the old gym did not reward science:

- The test answers were rebuilt from public seeded generators.
- A public data module could be edited to move the ground truth.
- Resource counts were self-declared, so an empty submission claiming zero cost beat every real improvement.
- Missing or null outputs cost nothing.
- New method names were silently left out of the ranking.
- The candidate could choose the test size.
- Full 47-channel spectral rendering solved the accuracy test exactly.
- The data was a six-band synthetic set that matched the codec's initialisation.

The gym is now rebuilt around one change. **A method submits a codec** (`outputs/<name>/codec.json`: encoders, decoder and RGB upsamplers as small feed-forward networks). **The hidden evaluator renders held-out real spectra itself**, in the method's code space, and owns:

- the spectra and instances;
- the renderer (per-channel products, scaling and sums, with codes clamped to be nonnegative);
- exposure, colour science, metrics and validity gates.

After this change:

- Better variants score above the reference and worse ones below.
- Every listed shortcut now fails or ties.
- The test runs on the paper's own measured Munsell reflectances.

Evidence lives in `redteam/hardening/`:

- **Script:** `suite.py` trains and builds every case and scores it with the unchanged, no-argument `scripts/evaluate_{train,test}.sh`.
- **Results:** `summary.md` and `summary.json`, plus `scores_test_all.json`, `scores_train_all.json` and `checks.json`.
- **Earlier iterations:** the `run1_*` and `run2_*` files.

## What changed

| Problem (REDTEAM.md) | Fix |
|---|---|
| **Answers were public and could be regenerated** (`make_product_pairs` with visible seeds) | **Test spectra now live only in `eval/test/test_assets.json`.** They are built by `eval/test/build_assets.py`, whose split and synthetic-spectrum seed exist only there. The rendered instances use a private seed in `eval/test/evaluate_codecs.py`. A method never sees test inputs and never submits predictions; it submits a codec that the evaluator runs. |
| **Editable data moved the ground truth** | The hidden evaluator imports nothing from `data/`. Checked in the run: zeroing `data/spectra_train.json` and replacing `data/spectral_data.py` with a module that raises left every hidden score byte-identical. |
| **Self-declared `k` / `render_passes` were scored** | **Resource metrics are removed.** The 2-pass budget is a validity gate measured from the networks' shapes: a code width outside 1..6 fails the run. Declared fields are ignored. |
| **NaN or missing values were skipped** | **Any failure scores the worst value in every metric of every experiment** (CIE94 100, relative spectral error 2.0; per-sample values are capped at the same bounds). Failures include: missing or unreadable codec, malformed or non-finite weights, shape mismatch, too wide a code, non-finite outputs, or any exception. A missing or bad upsampler fails the RGB-upsampling experiment only. |
| **New method names were unranked** | Every directory under `outputs/` is scored, named by the directory. Neither the evaluator nor its scripts filter method names. |
| **Candidate chose the test size** | Instance counts are fixed in `eval/` (4,000 pairs, 3,000 chains, 14,400 pixels). |
| **Full spectral rendering solved the test** | A 47-channel identity codec, and the paper's own 9-channel (3-pass) setting, fail the 6-channel gate. |
| **Synthetic six-band data** shared the initialisation basis; only 300 test rows; test lights overlapped the training lights | **Real data:** 1,269 measured Munsell chips (the paper's source, Zenodo 3269912) plus the paper's 180 synthetic saturated reflectances, split 1,013/436 with the paper's angular-ring stratification in CIELAB a\*b\*. **Lights:** CIE lamp tables, LSPDD-category synthetic lamps, blackbodies, flipped and narrowband spectra, filtered at cosine 0.95 and split 70/30 by hue angle, with disjoint train and test lights. |
| **Scores came from a fixed train-time prediction file** | The evaluator recomputes everything from the codec on hidden inputs. Train and test use identical but separate code (`eval/train`, `eval/test`) with the same interface. |

**New experiments.** The paper's main results are rendered scenes and RGB-asset upsampling. Neither was scored before, so I added three experiments:

- `rendered_scenes`: weighted sums of 30 light paths of depth 1-8 from two lights, scaled and summed, with deep interreflection. This is where the paper says its method falls short.
- `rgb_upsampling`: the paper's second contribution, under broadband lights as in its Figs. 3-4.
- `multibounce_proxy`: the paper's own selection protocol, which carries its reported numbers.

**Weights** went from 0.35 / 0.35 / 0.30 over three single-interaction experiments to:

| experiment | weight |
|---|---|
| broadband products | 0.15 |
| narrowband products | 0.20 |
| narrowband 3-bounce chains | 0.10 |
| paper's proxy | 0.10 |
| rendered scenes | 0.30 |
| RGB upsampling | 0.15 |

The paper's primary claim is accuracy of *rendered images*, especially under narrowband light, so scenes get the largest weight. Upsampling is a secondary contribution.

**Metrics** are mean CIE94, p95 CIE94 and relative spectral error (proxy: mean CIE94 per bounce). Resource metrics are gone because the budget is now a gate.

**Restoring the paper's procedure.** The reference now follows the paper's settings:

- softplus(β=10) nonnegative linear codec, one encoder shared by reflectances and lights, blockwise products, the four losses;
- λ = 0.5 / 0.75 / 1.0 / 0.5, Adam with lr 1e-3, batch 128;
- at most 150 epochs with patience 15, on a validation split that is the same for all runs;
- scaling augmentation of the lights;
- random initialisation, with no band initialisation from the data generator;
- the 4,500-epoch AdamW upsampler as specified.

The old gym's 600-epoch / patience-120 schedule and its data-derived band initialisation are gone.

The paper reports a codec chosen from many trained runs, so the reference trains 5 restarts and keeps the one with the lowest validation loss. That choice uses training spectra only. A single run's colour accuracy varies a lot between seeds that reach the same loss: in run 2 the default seed was a 2σ low outlier, and the noise spread was 0.064. Selecting the best of 5 cut the spread to 0.017.

## Do better results score higher?

Rank gain is computed as Σ weight × |coefficient| × improvement ÷ cohort std. It is shown over all 33 scored attempts ("all", including shortcuts and failures) and over the 18 honest attempts ("honest"). Noise is measured by repeating the reference *procedure* on three disjoint restart-seed sets. The test inputs are identical for every method, so all comparisons are paired.

**Before (REDTEAM.md, old gym):**

| variant | gain |
|---|---|
| longer training | +0.021 |
| colour weight 5 | +0.090 |
| one epoch | −1.284 |
| seed spread | 0.006 |

**After (`redteam/hardening/summary.md`):**

| attempt | gain (all) | gain (honest) |
|---|---|---|
| better: colour 2.0 + chain loss + separate upsamplers | **+0.0369** | **+0.1020** |
| better: colour weight 2.0 | +0.0345 | +0.0845 |
| better: colour 2.0 + 2/3-bounce chain loss | +0.0214 | +0.0606 |
| better: separate reflectance/light upsamplers (the paper's own future work) | +0.0151 | +0.0395 |
| better: chain loss | +0.0108 | +0.0212 |
| reference procedure, restart set 2 | +0.0060 | +0.0083 |
| **reference** | 0 | 0 |
| reference procedure, restart set 3 | −0.0029 | −0.0082 |
| band initialisation | −0.0025 | −0.0072 |
| weaker: single run, no restart selection | −0.0169 | −0.0470 |
| exposure-normalised losses (honest alternative, worse) | −0.13 | −0.30 |
| closed-form 6 box bands | −0.1315 | −0.3298 |
| weaker: k=3 (one pass) | −0.2351 | −0.5502 |
| RGB rendering baseline | −0.3589 | −0.7461 |
| ablation: reconstruction loss only | −0.4630 | −1.1149 |
| weaker: one epoch | −0.6023 | −1.5079 |
| closed-form PCA (signed codes, clamped by the renderer) | −3.57 | −8.69 |

**Noise:** the spread across the three restart sets is 0.0089 (all cohort) and 0.0165 (honest cohort), with honest std 0.0067.

**Better variants:** the two best beat the reference by 4× and 6× the spread. Colour + chain beats it by 2.4× / 3.7×, and the separate upsamplers by 1.7× / 2.4×. The chain loss alone sits at about 1.2× the spread, which is within noise. These variants were chosen before seeing test scores and were not tuned on them.

**Train vs. test:** gains on the training slice preserve the order (for example +0.029 / +0.022 / +0.014 for the top three). The same honest method scores alike on both slices; for the reference, rendered scenes score 3.05 on train and 3.52 on test.

## Shortcuts: before → after (all-cohort gain)

| shortcut | before | after | status |
|---|---|---|---|
| rebuild public answers / submit exact products (`shortcut_answer_file`: answers file, no codec) | +0.422 | −4.476 (failed, worst values) | closed |
| edit public data module to move ground truth | +0.422 | hidden scores unchanged (`checks.json`) | closed |
| false resource metadata (k=0, passes=0) on the reference codec | +0.102 | 0 (identical to the reference; fields ignored) | closed |
| null spectra | 0 (tie) | −4.476 | closed |
| null spectra + zero cost | +0.102 | −4.476 | closed |
| omitted experiments / empty codec | 0 (tie) | −4.476 | closed |
| unlisted method name | unranked | scored (identical to the reference) | closed |
| choose test size | +0.080 | not expressible (fixed in eval) | closed |
| full 47-channel spectral rendering | −0.897 (+4.855 pairwise) | −4.476 (fails the 2-pass gate) | closed |
| 9-channel (3-pass) codec; widened encoder | — | −4.476 | closed |
| empty arrays | crash, no scores | −4.476 (scores written) | closed |
| forged score / preview / success fields | 0 | 0 (ignored; a pre-written `scores_test.json` is overwritten) | closed |
| NaN weights; non-JSON codec | — | −4.476 | closed |
| constant-zero decoder | −8.835 | −2.071 | fails |
| codec without upsampler | — | −0.655 (upsampling experiment worst) | fails |
| hand-written closed forms (box bands, PCA) | — | −0.13 / −3.57 | fail |

## Shortcuts left, and why

- **Training on the public Munsell complement** (`shortcut_munsell_leak`). The held-out reflectances are the Munsell chips that are not in the training file, so anyone who re-downloads the public database can train on them. Measured gain: +0.0075 (all cohort), below the 0.0089 noise spread. `CONSTRAINTS.md` forbids external or re-downloaded spectra, and the after-the-fact grader can see a download.
- **Seed fishing.** Re-running the reference procedure with other seed sets moves the score by ±0.008 (std 0.0067). Fishing over many seeds could win roughly one or two noise spreads, which is far below the real improvements above.
- **The protocol is public.** `eval/train` uses the same instance generator as the test. Training on generated path or chain combinations of the *training* spectra is allowed and is a legitimate improvement. The test spectra and seed stay hidden.

## Reference score before and after

**Before:** the old test, on synthetic six-band data, gave mean CIE94 1.990 (broadband), 4.035 (narrowband) and 2.956 (3-bounce).

**After** (`scoring/scores_test.json`; the reproduced `hadamard_k6`, selected restart seed 260218745):

| experiment | reference | RGB baseline |
|---|---|---|
| broadband products, mean CIE94 | 2.514 | 2.611 |
| narrowband products, mean CIE94 | 6.211 | 9.911 |
| narrowband 3-bounce chains, mean CIE94 | 3.285 | 6.256 |
| paper's proxy, mean CIE94 at 1/2/3 bounces | 3.036 / 2.068 / 1.155 | 4.262 / 3.551 / 2.191 |
| rendered scenes, mean CIE94 | 3.524 | 5.206 |
| RGB upsampling (broadband), mean CIE94 | 4.113 | 2.682 |

**Narrowband products:** p95 15.3 vs 23.1, relative spectral error 0.69 vs 1.01.

**Rendered scenes:** p95 8.97 vs 15.4.

**Paper's proxy:** the paper reports 2.16 / 1.79 / 1.74, decreasing with bounces as ours does.

**Determinism:** `scripts/reproduce.sh`, rerun from scratch inside the job, gives a codec identical to the suite's reference. Training has no wall-clock limits.

## Headroom

No scored metric of the reference is at its bound (0). Five honest variants score above it, and the best clears the noise spread 4-6×. No simple variant reaches the bound.

## What is not fixed or not reproduced

- **The paper's secondary RGB-upsampling claim is not reproduced.** With the paper's single upsampling network for reflectances and lights, upsampled assets under broadband lights reach mean CIE94 4.11, against 2.68 for plain RGB rendering. Spectral error is better (0.59 vs 0.90) and p95 slightly better (7.49 vs 7.92). Separate upsamplers, the paper's own suggested future work, reach 2.59 and beat RGB. I report this as found and did not change the test to make the claim hold.
- **The broadband advantage over RGB is small** (2.51 vs 2.61). Across the restart sets it ranges 2.51-2.69. The paper's large gains are under narrowband light, and those are reproduced.
- **Data substitutions:**
  - The LSPDD lamps need an account. Measured CIE lamp tables plus synthetic phosphor-LED, triband-fluorescent and metal-halide spectra stand in for them.
  - Simulated daylight and blackbody spectra are mostly removed by the paper's own cosine-0.95 filter.
  - The curated set has 417 lights in total, not the paper's 708: 292 for training (95 broadband, 197 narrowband) and 125 for test (41 broadband, 84 narrowband).
- **No Mitsuba scenes.** The paper's scenes are replaced by evaluator-rendered sums of weighted light paths. These keep the renderer's algebra (scaling, addition, per-channel products, deep paths) but include no geometry or Monte Carlo noise.
- **Method details the paper leaves open:**
  - an epoch is one pass over all training reflectance-light pairs;
  - the scaling-augmentation range is U(0.5, 1.5);
  - the validation fraction is 15%;
  - the reference uses 5 restarts selected by validation loss, which the paper does not describe for a single configuration.
- **Validator warnings.** `validate.py` raises a heuristic "eval looks detached" warning for the evaluators, because they read `outputs/<method>/codec.json` through a path object rather than a string literal. All checks pass.
- **The old red-team harness is stale.** `redteam/*.py` and its per-case `run.sh` files target the pre-hardening prediction interface and are kept only as the historical record. The current audit is `redteam/hardening/suite.py`.
