#!/bin/bash
# Hidden held-out evaluation. Takes no arguments: scores every method
# directory under outputs/ (each must hold a codec.json) on held-out spectra
# and writes scoring/scores_test.json. Failed or missing submissions receive
# the worst value of every metric.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p scoring

python eval/test/evaluate_codecs.py "$@" --output scoring/scores_test.json
