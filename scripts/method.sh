#!/bin/bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

OUT="${1:-outputs/hadamard_k6}"
EPOCHS="${EPOCHS:-180}"
DEVICE="${DEVICE:-cpu}"
python method/train_codec.py --output "$OUT" --epochs "$EPOCHS" --device "$DEVICE"
if [ "${EVALUATE_AFTER:-1}" = "1" ]; then
  bash scripts/evaluate.sh "$OUT" outputs/rgb_baseline
fi
