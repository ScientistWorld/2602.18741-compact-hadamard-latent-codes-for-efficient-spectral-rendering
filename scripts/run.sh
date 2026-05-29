#!/bin/bash
# Example job script submitted via the end-of-turn YAML block.
#
# This runs inside the compute container with:
#   - Your workspace mounted at /home/user
#   - GPU(s) available
#   - No internet access
#
# Make sure all data, code, and dependencies are already in the
# workspace or baked into the container before submitting.

set -e

cd /home/user

python - <<'PY'
import numpy
import torch
print("numpy", numpy.__version__)
print("torch", torch.__version__)
PY

bash scripts/evaluate.sh outputs/hadamard_k6 outputs/rgb_upsampler_k6 outputs/rgb_baseline
python validate.py --compare
