#!/bin/bash
# Train the paper's method: the k=6 nonnegative linear Hadamard codec
# (method/train_codec.py, paper settings by default) and its RGB-to-latent
# upsampler (method/train_upsampler.py). Writes <out>/codec.json.
#
# Usage: bash scripts/method.sh [output_dir]   (extra codec flags via CODEC_ARGS)

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

OUT="${1:-outputs/hadamard_k6}"
python method/train_codec.py --output "$OUT" ${CODEC_ARGS:-}
python method/train_upsampler.py --codec-dir "$OUT"
