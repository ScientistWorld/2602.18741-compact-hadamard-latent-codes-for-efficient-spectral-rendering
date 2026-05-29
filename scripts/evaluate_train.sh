#!/bin/bash
# Train-slice evaluation entry point.
#
# Mirrors scripts/evaluate.sh: pass output directories containing
# predictions.json files, or pass no arguments to enumerate outputs/*.

set -e

cd /home/user

mkdir -p scoring

python eval/train/evaluate_predictions.py "$@" --output scoring/scores_train.json
