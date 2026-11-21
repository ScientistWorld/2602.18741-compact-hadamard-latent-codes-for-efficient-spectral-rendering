#!/bin/bash
# Hardening job: build the spectral libraries from the raw public data, then
# train/score the reference, variants, baselines and shortcuts through the
# hidden test (redteam/hardening/suite.py), which finishes by reproducing the
# reference end to end with scripts/reproduce.sh.

set -euo pipefail

cd /home/user

python eval/test/build_assets.py
python redteam/hardening/suite.py
