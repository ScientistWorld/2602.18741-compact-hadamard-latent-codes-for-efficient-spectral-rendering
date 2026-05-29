#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and should call
# scripts/baseline.sh and scripts/method.sh to run baselines and
# the paper's method, each of which calls scripts/evaluate.sh.
#
# Assumes:
#   - Container is built (environment/container.sif)
#   - Data and models are downloaded (via scripts/download.sh)
#   - Working directory is /home/user
#
# This is the "gold standard" reproduction — 
# You do not need to run this, but keep this in good shape
# so other agents can easily run a full loop of reproduction and get the paper's numbers.

set -e

cd /home/user

EVALUATE_AFTER=0 bash scripts/baseline.sh outputs/rgb_baseline
EVALUATE_AFTER=0 K=6 bash scripts/method.sh outputs/hadamard_k6
if [ "${TRAIN_K9:-1}" = "1" ]; then
  EVALUATE_AFTER=0 K=9 bash scripts/method.sh outputs/hadamard_k9
fi
python method/train_upsampler.py \
  --codec outputs/hadamard_k6/codec.pt \
  --output outputs/rgb_upsampler_k6 \
  --epochs "${UPSAMPLER_EPOCHS:-1200}" \
  --device "${DEVICE:-cpu}"
if [ "${TRAIN_K9:-1}" = "1" ]; then
  bash scripts/evaluate.sh outputs/hadamard_k6 outputs/hadamard_k9 outputs/rgb_upsampler_k6 outputs/rgb_baseline
else
  bash scripts/evaluate.sh outputs/hadamard_k6 outputs/rgb_upsampler_k6 outputs/rgb_baseline
fi
