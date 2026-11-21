"""Run independent attempts with the unchanged hidden entry point, no arguments.

Only this harness sees hidden scoring outputs. Candidate code is methods.py or
train_variant.py. Each evaluator invocation starts a new Python process; no
candidate process, monkeypatch, or interpreter state survives into it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "redteam"
SEED = 260218741
CASES = [
    "reference", "reference_seed1", "reference_seed2", "reference_seed3",
    "better_long", "better_color", "weaker_one_epoch", "honest_rgb", "honest_six_samples",
    "shortcut_full_spectral", "shortcut_target_copy", "shortcut_metadata",
    "shortcut_null", "shortcut_null_zero_cost", "shortcut_omitted",
    "shortcut_unlisted_name", "shortcut_empty_rows", "shortcut_forged_fields",
    "shortcut_constant_zero", "shortcut_copy_input", "shortcut_test_size", "shortcut_ground_truth",
]
RESTORE = ["data/spectral_common.py", "scoring/scores_train.json", "scoring/scores_test.json"]


def call(command, log, timeout=3000):
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            timeout=timeout, env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"})
    return {"exit_code": result.returncode, "wall_seconds": time.monotonic() - start}


def ensure_reference(log):
    cache = AUDIT / ".cache/reference"
    if (cache / "predictions.json").exists() and (cache / "codec.pt").exists():
        return
    source = ROOT / "outputs/hadamard_k6"
    cache.mkdir(parents=True, exist_ok=True)
    if (source / "predictions.json").exists() and (source / "codec.pt").exists():
        for file in ["predictions.json", "codec.pt"]:
            shutil.copy2(source / file, cache / file)
    else:
        result = call([sys.executable, "redteam/train_variant.py", str(cache)], log)
        if result["exit_code"]:
            raise RuntimeError("Cannot construct reference")


def run_case(name):
    os.chdir(ROOT)
    out = AUDIT / name
    out.mkdir(parents=True, exist_ok=True)
    with (out / "run.log").open("w") as log:
        ensure_reference(log)
        backup = AUDIT / ".original"
        if backup.exists():
            raise RuntimeError("Unrestored prior run: inspect redteam/.original")
        backup.mkdir()
        original_exists = {}
        for relative in RESTORE:
            source = ROOT / relative
            original_exists[relative] = source.exists()
            if source.exists():
                destination = backup / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        had_outputs = (ROOT / "outputs").exists()
        if had_outputs:
            shutil.move(ROOT / "outputs", backup / "outputs")
        (ROOT / "outputs").mkdir()
        (ROOT / "scoring/scores_train.json").unlink(missing_ok=True)
        (ROOT / "scoring/scores_test.json").unlink(missing_ok=True)
        status = {"case": name, "candidate_method": "hadamard_k6", "test_command": "bash scripts/evaluate_test.sh", "hidden_arguments": []}
        test_script = ROOT / "scripts/evaluate_test.sh"
        hidden_code = ROOT / "eval/test/evaluate_predictions.py"
        status["evaluator_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [test_script, hidden_code]}
        try:
            result = call([sys.executable, "baseline/rgb_baseline.py"], log)
            if result["exit_code"]:
                raise RuntimeError("Baseline failed")
            candidate = ROOT / "outputs/hadamard_k6"
            if name == "reference":
                shutil.copytree(AUDIT / ".cache/reference", candidate)
            elif name in {"reference_seed1", "reference_seed2", "reference_seed3", "better_long", "better_color", "weaker_one_epoch"}:
                seed = SEED + int(name[-1]) - 1 if name.startswith("reference_seed") else SEED
                epochs = 6000 if name.startswith("better_") else 1 if name.startswith("weaker_") else 600
                command = [sys.executable, "redteam/train_variant.py", str(candidate), "--seed", str(seed), "--epochs", str(epochs)]
                if name.startswith("better_"):
                    command += ["--patience", "0"]
                if name == "better_color":
                    command += ["--color-weight", "5.0"]
                status["training"] = call(command, log)
                if status["training"]["exit_code"]:
                    raise RuntimeError("Training failed")
            else:
                # Run the candidate in a separate process. The candidate cannot
                # leave any Python monkeypatch active in the test evaluator.
                status["candidate"] = call([sys.executable, "redteam/install_candidate.py", name, str(candidate), str(out / "candidate_notes.json")], log)
                if status["candidate"]["exit_code"]:
                    raise RuntimeError("Candidate failed")
            artifacts = out / "artifacts"
            status["candidate_method"] = json.loads((candidate / "predictions.json").read_text())["method"]
            if artifacts.exists():
                shutil.rmtree(artifacts)
            shutil.copytree(candidate, artifacts)
            status["train_evaluation"] = call(["bash", "scripts/evaluate_train.sh"], log)
            if (ROOT / "scoring/scores_train.json").exists():
                shutil.copy2(ROOT / "scoring/scores_train.json", out / "scores_train.json")
            if (ROOT / "scoring/scores_test.json").exists():
                shutil.copy2(ROOT / "scoring/scores_test.json", out / "shortcut_pretest_scores.json")
            status["test_evaluation"] = call(["bash", "scripts/evaluate_test.sh"], log)
            status["test_wrote_scores"] = (ROOT / "scoring/scores_test.json").exists()
            if status["test_wrote_scores"]:
                shutil.copy2(ROOT / "scoring/scores_test.json", out / "scores_test.json")
            # Check without changing evaluator files.
            for p in [test_script, hidden_code]:
                assert hashlib.sha256(p.read_bytes()).hexdigest() == status["evaluator_sha256"][str(p.relative_to(ROOT))]
        finally:
            shutil.rmtree(ROOT / "outputs")
            if had_outputs:
                shutil.move(backup / "outputs", ROOT / "outputs")
            for relative in RESTORE:
                if original_exists[relative]:
                    shutil.copy2(backup / relative, ROOT / relative)
                else:
                    (ROOT / relative).unlink(missing_ok=True)
            shutil.rmtree(backup)
            (out / "status.json").write_text(json.dumps(status, indent=2))
    print(json.dumps(status), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES + ["suite"])
    args = parser.parse_args()
    if args.case == "suite":
        for name in CASES:
            if (AUDIT / name / "status.json").exists():
                print("Already complete:", name, flush=True)
                continue
            try:
                run_case(name)
            except Exception as exc:
                print("Case failed:", name, repr(exc), flush=True)
        subprocess.run([sys.executable, "redteam/summarize.py"], cwd=ROOT, check=True)
    else:
        run_case(args.case)


if __name__ == "__main__":
    main()
