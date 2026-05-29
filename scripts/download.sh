#!/bin/bash
# Download all data and models needed for this environment.
#
# Run on a node with internet access BEFORE building the container
# or submitting compute jobs.
#
# This script should be idempotent — safe to run multiple times.
# It should skip files that already exist.
#
# Update the storage estimate below as you add downloads.
#
# Estimated total download size: 0 GB
# Estimated disk usage after extraction: 0 GB
#
# No public external data or model artifact is required for this reproduction.
# The benchmark spectra are generated deterministically from tracked code.

set -e

cd /home/user

mkdir -p data/downloads
echo "No external downloads are required. The spectral benchmark is generated deterministically by data/spectral_common.py."
