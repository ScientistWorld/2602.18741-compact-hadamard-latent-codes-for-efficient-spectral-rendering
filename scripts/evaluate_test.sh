#!/bin/bash
# Held-out test-slice evaluation entry point.
#
# Mirrors scripts/evaluate.sh, but writes scoring/scores_test.json and uses
# scoring/scores_train.json, when present, to score the same method set.

set -e

cd /home/user

mkdir -p scoring

python eval/test/evaluate_predictions.py "$@" \
  --output scoring/scores_test.json \
  --match-train scoring/scores_train.json
