#!/usr/bin/env python3
"""Hardening audit: reference, variants, baselines and shortcuts through the hidden test.

1. Trains every method attempt with the final method code into runs/<case>/
   (resumable; independent cases run in parallel, each single-threaded and
   seeded, so results do not depend on machine load).
2. Builds closed-form codecs and shortcut submissions.
3. Installs every attempt as outputs/<case>/ and runs the unchanged
   ``bash scripts/evaluate_train.sh`` and ``bash scripts/evaluate_test.sh``
   with no arguments, keeping copies of both score files.
4. Checks that a pre-written score file is overwritten and that tampering with
   the public data/ files cannot change hidden-test scores.
5. Restores outputs/ by re-running ``scripts/reproduce.sh`` from scratch
   (reference + RGB baseline only) and checks it matches runs/reference.
6. Summarises rank gains (summarize.py).
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = HERE / "runs"
LOGS = HERE / "logs"
SEED = 260218741
PY = sys.executable

TRAINED = {
    # Every codec uses train_codec.py's default protocol (5 restarts, lowest validation loss kept)
    # unless --restarts is given. The reference procedure is repeated on disjoint restart seeds.
    "reference": [],
    "reference_seedset2": ["--seed", str(SEED + 5)],
    "reference_seedset3": ["--seed", str(SEED + 10)],
    "better_color": ["--lambda-col", "2.0"],
    "better_sep_upsampler": [],
    "better_color_chain": ["--lambda-col", "2.0", "--lambda-chain", "0.5"],
    "better_color_chain_sep": ["--lambda-col", "2.0", "--lambda-chain", "0.5"],
    "better_chain": ["--lambda-chain", "0.5"],
    "better_exposure": ["--exposure-normalize"],
    "better_chain_exposure": ["--lambda-chain", "0.5", "--exposure-normalize"],
    "variant_band_init": ["--init", "bands"],
    "variant_single_run": ["--restarts", "1"],
    "weaker_one_epoch": ["--epochs", "1", "--restarts", "1"],
    "weaker_k3": ["--k", "3"],
    "ablation_rec_only": ["--lambda-e2e", "0", "--lambda-code", "0", "--lambda-col", "0", "--lambda-rec", "1"],
    "shortcut_munsell_leak": ["--extra-reflectances-from", "eval/test/test_assets.json"],
    "shortcut_k9": ["--k", "9", "--restarts", "1"],
}
NO_UPSAMPLER = {"shortcut_k9"}
UPSAMPLER_ARGS = {"better_sep_upsampler": ["--separate"], "better_color_chain_sep": ["--separate"]}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd: list[str], logfile: Path, check: bool = True) -> int:
    with logfile.open("a") as fh:
        fh.write(f"$ {' '.join(cmd)}\n")
        fh.flush()
        rc = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}).returncode
    if check and rc:
        raise RuntimeError(f"command failed ({rc}): {' '.join(cmd)} -- see {logfile}")
    return rc


def seed_of(args: list[str]) -> int:
    return int(args[args.index("--seed") + 1]) if "--seed" in args else SEED


def train_case(case: str, args: list[str]) -> str:
    out = RUNS / case
    if (out / "done.json").exists():
        return f"{case}: cached"
    out.mkdir(parents=True, exist_ok=True)
    logfile = LOGS / f"{case}.log"
    logfile.write_text("")
    start = time.time()
    run([PY, "method/train_codec.py", "--output", str(out), "--method-name", case] + args, logfile)
    if case not in NO_UPSAMPLER:
        run([PY, "method/train_upsampler.py", "--codec-dir", str(out), "--seed", str(seed_of(args))] + UPSAMPLER_ARGS.get(case, []), logfile)
    (out / "done.json").write_text(json.dumps({"seconds": time.time() - start, "args": args}))
    return f"{case}: trained in {time.time() - start:.0f}s"


def load_train_json() -> dict:
    return json.loads((ROOT / "data/spectra_train.json").read_text())


def closed_form_case(case: str) -> str:
    out = RUNS / case
    if (out / "done.json").exists():
        return f"{case}: cached"
    out.mkdir(parents=True, exist_ok=True)
    logfile = LOGS / f"{case}.log"
    logfile.write_text("")
    lib = load_train_json()
    mask = np.asarray(lib["visible_mask"]) > 0
    vis = np.flatnonzero(mask)
    if case == "closed_box6":
        enc = np.zeros((6, mask.size))
        dec = np.zeros((mask.size, 6))
        for j, group in enumerate(np.array_split(vis, 6)):
            enc[j, group] = 1.0 / len(group)
            dec[group, j] = 1.0
    elif case == "closed_pca6":
        x = np.concatenate([np.asarray(lib["reflectances"]), np.asarray(lib["illuminants"])])
        _, _, vt = np.linalg.svd(x, full_matrices=False)
        enc = vt[:6]
        dec = vt[:6].T
    else:
        raise ValueError(case)
    (out / "codec.json").write_text(json.dumps({"method": case, "encoder": enc.tolist(), "decoder": dec.tolist()}))
    run([PY, "method/train_upsampler.py", "--codec-dir", str(out)], logfile)
    (out / "done.json").write_text(json.dumps({"closed_form": case}))
    return f"{case}: built"


def baseline_case() -> str:
    out = RUNS / "rgb_baseline"
    if (out / "done.json").exists():
        return "rgb_baseline: cached"
    logfile = LOGS / "rgb_baseline.log"
    logfile.write_text("")
    run([PY, "baseline/rgb_baseline.py", "--output", str(out)], logfile)
    (out / "done.json").write_text("{}")
    return "rgb_baseline: built"


def shortcut_cases() -> list[str]:
    ref = json.loads((RUNS / "reference" / "codec.json").read_text())
    k = len(ref["encoder"])
    made = {}

    def put(name: str, codec, extra_files: dict | None = None) -> None:
        out = RUNS / name
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        if codec is not None:
            text = codec if isinstance(codec, str) else json.dumps(codec)
            (out / "codec.json").write_text(text)
        for fname, content in (extra_files or {}).items():
            (out / fname).write_text(content)
        made[name] = True

    eye = np.eye(47).tolist()
    put("shortcut_full_spectral", {"method": "full_spectral", "encoder": eye, "decoder": eye, "upsampler": np.zeros((47, 3)).tolist()})
    nan = copy.deepcopy(ref)
    nan["decoder"][10][0] = float("nan")
    put("shortcut_nan_weights", json.dumps(nan))  # json.dumps writes NaN literally
    null = copy.deepcopy(ref)
    null["decoder"] = [[None] * k for _ in range(47)]
    null["encoder"] = [[None] * 47 for _ in range(k)]
    put("shortcut_null_weights", null)
    put("shortcut_empty_codec", {})
    put("shortcut_empty_rows", {"encoder": [], "decoder": [], "upsampler": []})
    put("shortcut_not_json", "this is not a codec")
    answers = {"method": "answer_file", "experiments": {"spectral_product_broadband": {"pred_spectrum": [[0.0] * 47]}}}
    put("shortcut_answer_file", None, {"predictions.json": json.dumps(answers)})
    meta = copy.deepcopy(ref)
    meta.update(k=0, render_passes=0, latent_channels=0, output_wavelengths=47)
    put("shortcut_metadata", meta)
    forged = copy.deepcopy(ref)
    forged.update(
        scores={"mean_delta_e94": 0.0}, mean_delta_e94=0.0, spectral_nrmse=0.0, status="ok", success=True,
        test_size=2, target_spectrum=[[0.0] * 47], experiments={"rendered_scenes": {"mean_delta_e94": 0.0}},
    )
    put("shortcut_forged_fields", forged)
    put("zz_unlisted_method_name", copy.deepcopy(ref))
    zero = copy.deepcopy(ref)
    zero["decoder"] = np.zeros((47, k)).tolist()
    put("shortcut_constant_zero", zero)
    noup = copy.deepcopy(ref)
    noup.pop("upsampler", None)
    put("shortcut_no_upsampler", noup)
    deep = copy.deepcopy(ref)  # 9 channels hidden behind a 6-channel interface is impossible: widen encoder only
    deep["encoder"] = deep["encoder"] + deep["encoder"][:3]
    put("shortcut_wide_encoder", deep)
    return sorted(made)


def smoke() -> None:
    """Seconds-long end-to-end check before the long training stage."""
    tmp = RUNS / "_smoke"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    logfile = LOGS / "smoke.log"
    logfile.write_text("")
    run([PY, "baseline/rgb_baseline.py", "--output", str(tmp / "rgb")], logfile)
    run([PY, "method/train_codec.py", "--output", str(tmp / "codec"), "--epochs", "2", "--max-steps-per-epoch", "5"], logfile)
    run([PY, "method/train_upsampler.py", "--codec-dir", str(tmp / "codec"), "--epochs", "2"], logfile)
    for ev in ("eval/train/evaluate_codecs.py", "eval/test/evaluate_codecs.py"):
        out = tmp / "scores.json"
        run([PY, ev, str(tmp / "rgb"), str(tmp / "codec"), str(tmp / "missing"), "--output", str(out)], logfile)
        diag = json.loads(out.read_text())["_diagnostics"]["methods"]
        if diag["rgb"]["status"] != "ok" or diag["codec"]["status"] != "ok" or diag["missing"]["status"] != "failed":
            raise RuntimeError(f"smoke evaluation failed: {json.dumps(diag)}")
        log(f"smoke {ev}: {json.dumps(json.loads(out.read_text())['experiments']['rendered_scenes'])}")
    shutil.rmtree(tmp)


def run_parallel(jobs, workers: int) -> None:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [(a, pool.submit(fn, *a)) for fn, *a in jobs]
        for a, fut in futures:
            try:
                log(fut.result())
            except Exception as exc:  # the attempt then has no codec and scores as failed
                log(f"FAILED {a[0]}: {exc}")


def install(cases: list[str]) -> None:
    out = ROOT / "outputs"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for case in cases:
        dest = out / case
        dest.mkdir()
        for f in (RUNS / case).iterdir():
            if f.name in ("codec.json", "predictions.json"):
                shutil.copy2(f, dest / f.name)


def evaluate(tag: str) -> tuple[dict, dict]:
    logfile = LOGS / f"evaluate_{tag}.log"
    run(["bash", "scripts/evaluate_train.sh"], logfile)
    run(["bash", "scripts/evaluate_test.sh"], logfile)
    train = json.loads((ROOT / "scoring/scores_train.json").read_text())
    test = json.loads((ROOT / "scoring/scores_test.json").read_text())
    return train, test


def main() -> None:
    RUNS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    try:
        cpus = len(os.sched_getaffinity(0))
    except AttributeError:
        cpus = os.cpu_count() or 1
    workers = max(1, min(cpus, 16))
    log(f"workers={workers}")

    # Keep the pre-hardening outputs out of the way (old prediction format).
    old = ROOT / "outputs"
    if old.exists() and not (ROOT / "tmp/outputs_pre_hardening").exists():
        (ROOT / "tmp").mkdir(exist_ok=True)
        shutil.move(str(old), ROOT / "tmp/outputs_pre_hardening")

    smoke()
    order = ["reference", "reference_seedset2", "reference_seedset3", "better_color", "better_color_chain_sep",
             "better_color_chain", "better_chain", "better_sep_upsampler", "better_exposure", "better_chain_exposure",
             "variant_band_init", "weaker_k3", "ablation_rec_only", "shortcut_munsell_leak", "variant_single_run",
             "weaker_one_epoch", "shortcut_k9"]
    jobs = [(baseline_case,), (closed_form_case, "closed_box6"), (closed_form_case, "closed_pca6")]
    jobs = [(train_case, c, TRAINED[c]) for c in order] + jobs
    run_parallel(jobs, workers)
    shortcuts = shortcut_cases()

    cases = sorted(set(TRAINED) | {"rgb_baseline", "closed_box6", "closed_pca6"} | set(shortcuts))
    checks: dict = {}
    scoring = ROOT / "scoring"
    saved = {name: (scoring / name).read_bytes() for name in ("scores_train.json", "scores_test.json") if (scoring / name).exists()}
    try:
        install(cases)
        fake = {"experiments": {"rendered_scenes": {"results": {"forged_prewritten_method": {"mean_delta_e94": 0.0}}}}}
        (scoring / "scores_test.json").write_text(json.dumps(fake))
        train, test = evaluate("all")
        (HERE / "scores_train_all.json").write_text(json.dumps(train, indent=2, sort_keys=True))
        (HERE / "scores_test_all.json").write_text(json.dumps(test, indent=2, sort_keys=True))
        checks["prewritten_score_file_overwritten"] = all(
            "forged_prewritten_method" not in exp["results"] for exp in test["experiments"].values()
        )
        checks["methods_scored"] = sorted(test["experiments"]["rendered_scenes"]["results"])

        # Tamper with every public data file the method side can edit; hidden scores must not move.
        data_files = [ROOT / "data/spectra_train.json", ROOT / "data/spectral_data.py"]
        backup = {p: p.read_bytes() for p in data_files}
        try:
            lib = json.loads(backup[data_files[0]])
            lib["reflectances"] = [[0.0] * 47 for _ in lib["reflectances"]]
            lib["illuminants"] = [[0.0] * 47 for _ in lib["illuminants"]]
            lib["cmf_xyz"] = [[0.0] * 47 for _ in range(3)]
            data_files[0].write_text(json.dumps(lib))
            data_files[1].write_text("raise RuntimeError('tampered public data module')\n")
            install(["reference"])
            run(["bash", "scripts/evaluate_test.sh"], LOGS / "evaluate_tamper.log")
            tampered = json.loads((scoring / "scores_test.json").read_text())
        finally:
            for p, content in backup.items():
                p.write_bytes(content)
        same = all(
            tampered["experiments"][e]["results"]["reference"] == test["experiments"][e]["results"]["reference"]
            for e in test["experiments"]
        )
        checks["public_data_tamper_changes_hidden_scores"] = not same
    finally:
        for name, content in saved.items():
            (scoring / name).write_bytes(content)

    # Restore outputs/ to the reference runs by reproducing them from scratch with the final code.
    out = ROOT / "outputs"
    if out.exists():
        shutil.rmtree(out)
    rlog = LOGS / "reproduce.log"
    rlog.write_text("")
    run(["bash", "scripts/reproduce.sh"], rlog)
    repro = json.loads((ROOT / "outputs/hadamard_k6/codec.json").read_text())
    cached = json.loads((RUNS / "reference/codec.json").read_text())
    checks["reproduce_matches_suite_reference"] = all(
        np.allclose(np.asarray(repro[key], dtype=float), np.asarray(cached[key], dtype=float), rtol=0, atol=1e-9)
        for key in ("encoder", "decoder")
    )
    checks["final_outputs"] = sorted(p.name for p in out.iterdir())
    (HERE / "checks.json").write_text(json.dumps(checks, indent=2))
    log(json.dumps(checks))
    run([PY, str(HERE / "summarize.py")], LOGS / "summarize.log")
    log((HERE / "summary.md").read_text())


if __name__ == "__main__":
    main()
