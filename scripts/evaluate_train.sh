#!/bin/bash
# Training-slice evaluation (public). With no arguments it scores every
# method directory under outputs/ on the training spectra and writes
# scoring/scores_train.json. Same interface and protocol as the test slice.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p scoring

python eval/train/evaluate_codecs.py "$@" --output scoring/scores_train.json
