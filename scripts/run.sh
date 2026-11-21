#!/bin/bash
# Compute-node entry point: reproduce the reference end to end (RGB baseline,
# the paper's k=6 codec with its RGB upsampler, train/test scoring).
#
# The hardening audit that trains and scores every variant and shortcut is
# `python redteam/hardening/suite.py` (see HARDENING.md).

set -euo pipefail

cd /home/user

bash scripts/reproduce.sh
