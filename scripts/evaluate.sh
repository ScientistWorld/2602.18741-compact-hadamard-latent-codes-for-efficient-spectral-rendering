#!/bin/bash
# Standard evaluation entry point. Scores every method directory under
# outputs/ (each holding a codec.json, see briefing/evaluation.md) on the
# training slice and, when the held-out evaluator is present, on the test
# slice. scoring/scores.json mirrors the held-out scores (or the training
# scores when the held-out evaluator is not available).

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p scoring

bash scripts/evaluate_train.sh
if [ -f eval/test/evaluate_codecs.py ] && [ -f eval/test/test_assets.json ]; then
  bash scripts/evaluate_test.sh
  cp scoring/scores_test.json scoring/scores.json
else
  cp scoring/scores_train.json scoring/scores.json
fi
