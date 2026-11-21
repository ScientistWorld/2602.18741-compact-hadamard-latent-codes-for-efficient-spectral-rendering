"""Candidate process ends before either evaluator starts."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from methods import create

name, destination, notes = sys.argv[1:]
Path(notes).write_text(json.dumps(create(name, Path(destination)), indent=2))
