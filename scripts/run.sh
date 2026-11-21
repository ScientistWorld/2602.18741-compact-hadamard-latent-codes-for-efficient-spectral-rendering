#!/bin/bash
# Temporary audit job. Restored after the audit completes.

set -euo pipefail

cd /home/user

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
python redteam/data_checks.py
python redteam/audit.py suite
