#!/bin/bash
# Reproduce the reference end to end: RGB baseline, the paper's k=6 codec and
# upsampler, then train/test scoring of every method under outputs/.
#
# Assumes the committed spectral libraries (data/spectra_train.json and the
# held-out library). To rebuild them from the public raw sources run
# `bash scripts/download.sh` and `python eval/test/build_assets.py` first.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

bash scripts/baseline.sh outputs/rgb_baseline
bash scripts/method.sh outputs/hadamard_k6
bash scripts/evaluate.sh
