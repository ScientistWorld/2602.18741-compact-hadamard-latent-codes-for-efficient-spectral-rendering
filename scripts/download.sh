#!/bin/bash
# Download the public raw spectral data used to build this benchmark.
#
# Run on a node with internet access BEFORE building the container or
# submitting compute jobs. Idempotent: every file is skipped if present.
#
# Estimated total download size: ~1.3 MB
# Estimated disk usage after download: ~1.3 MB (files are read gzip-compressed)
#
# Sources (all public):
#   - Munsell Colors Matt (spectrophotometer measured), 1269 chips,
#     380-800 nm at 1 nm, University of Eastern Finland spectral database,
#     mirrored on Zenodo record 3269912 (the paper's reflectance source).
#   - CIE data tables (files.cie.co.at): CIE 1931 2-degree colour-matching
#     functions, standard illuminants A and D65, daylight components S0/S1/S2,
#     indoor daylight ID65, and the CIE fluorescent (FL1-FL12, FL3.1-FL3.15),
#     high-pressure discharge (HP1-HP5) and LED (LED-B1..B5, BH1, RGB1, V1, V2)
#     lamp tables. These stand in for the paper's LSPDD lamp database, which
#     requires an account.
#
# The curated spectra derived from these files are committed to git
# (data/spectra_train.json and the hidden test library), so the files below
# are only needed to rebuild them with the dataset builder.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RAW="$REPO_ROOT/data/downloads/raw"
mkdir -p "$RAW"

fetch() {
  local url="$1" dest="$2"
  if [ -s "$dest" ]; then
    echo "present: $dest"
    return
  fi
  echo "fetching: $url"
  curl -fsSL --retry 3 -o "$dest.part" "$url"
  mv "$dest.part" "$dest"
}

fetch "https://zenodo.org/api/records/3269912/files/munsell380_800_1.asc.gz/content" "$RAW/munsell380_800_1.asc.gz"
fetch "https://zenodo.org/api/records/3269912/files/README.txt/content" "$RAW/munsell_README.txt"

CIE="https://files.cie.co.at/Publications-datasets"
for f in \
  CIE_xyz_1931_2deg.csv \
  CIE_std_illum_D65.csv \
  CIE_std_illum_A_1nm.csv \
  CIE_illum_Dxx_comp.csv \
  CIE_illum_ID65.csv \
  CIE_illum_FLs.csv \
  CIE_illum_HPs.csv \
  CIE_illum_LEDs.csv; do
  fetch "$CIE/$f" "$RAW/$f"
done

echo "Raw spectral data ready in $RAW"
