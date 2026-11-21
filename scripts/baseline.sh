#!/bin/bash
# Standard RGB rendering baseline expressed as a 3-channel, one-pass codec.
#
# Usage: bash scripts/baseline.sh [output_dir]

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

OUT="${1:-outputs/rgb_baseline}"
python baseline/rgb_baseline.py --output "$OUT"
