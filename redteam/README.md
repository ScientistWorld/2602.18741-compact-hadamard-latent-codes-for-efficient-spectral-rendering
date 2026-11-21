Run `python redteam/audit.py suite` in the gym container on a compute node, or
run any individual `redteam/<attempt>/run.sh`. No package installation is needed.

Each attempt installs its candidate outputs, evaluates the public training
slice, and launches the unchanged `bash scripts/evaluate_test.sh` with no
arguments in a separate process. Its folder records both score files, exit
codes, evaluator hashes, and logs. Candidate installation uses only public
data/method code and the reference outputs whose reuse the audit permits.
The hidden evaluator and reference schema are used only by the audit harness
and reporting code, never to construct candidate predictions.

The harness temporarily isolates `outputs/` and preserves/restores the
original data module and score files for every attempt. Generated predictions,
checkpoints, caches, and temporary snapshots are gitignored here. The final
report and small score records are tracked. No evaluator, Python environment,
container, or running process is modified.

Honest variants: the original 600-epoch codec at three optimizer/sampling
seeds, with the original dataset fixed; 6,000 training epochs; 6,000 epochs
with stronger color supervision; one training epoch; the real RGB baseline;
and a fixed six-wavelength interpolation baseline. No honest variant selects
its parameters using the hidden test.

Shortcut candidates cover full spectral brute force, publicly rebuilt
answers, false resource counts, null predictions, absent experiments,
unrecognized method names, empty arrays, forged preview/target/success fields,
constant or copied-input outputs, choosing the evaluation size, and replacing
the supplied data-generation asset. Even ties are called shortcuts; forged
field controls that tie merely reproduce the original predictions.

`summary.json` and `summary.csv` use absolute reference coefficients, their
`higher_is_better` directions, experiment weights, and per-metric population
standard deviations over the explicit successful audit cohort. Pairwise
scores use the reference and that attempt only. The future cohort is not
known, so its precise normalized ranks cannot be predicted. Componentwise
dominance and zero-contribution missing metrics do not need that assumption.
