"""Public-data diagnostics, run on the compute node."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from data.spectral_common import make_dataset, WAVELENGTHS, VISIBLE_MASK

ds = make_dataset()
train = {row.tobytes() for row in ds.illumination_train}
result = {
    "illumination_train_count": len(ds.illumination_train),
    "broadband_test_count": len(ds.illumination_test_broadband),
    "broadband_test_also_in_train": sum(row.tobytes() in train for row in ds.illumination_test_broadband),
    "narrowband_test_count": len(ds.illumination_test_narrowband),
    "narrowband_test_also_in_train": sum(row.tobytes() in train for row in ds.illumination_test_narrowband),
    "reflectance_train_count": len(ds.reflectance_train),
    "reflectance_test_count": len(ds.reflectance_test),
    "reflectance_test_also_in_train": sum(row.tobytes() in {item.tobytes() for item in ds.reflectance_train} for row in ds.reflectance_test),
    "active_wavelengths": int(VISIBLE_MASK.sum()),
    "total_wavelengths": len(WAVELENGTHS),
}
(ROOT / "redteam/data_checks.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
