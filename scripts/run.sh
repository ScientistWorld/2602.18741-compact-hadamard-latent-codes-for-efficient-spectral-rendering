#!/bin/bash
# Compute-node entry point for the train/test evaluation split.

set -euo pipefail

cd /home/user

bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
