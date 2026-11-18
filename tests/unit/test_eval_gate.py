from pathlib import Path

import pytest

from jobfit.adapters.taxonomy_file import load_default_taxonomy
from jobfit.eval.dataset import load_cases
from jobfit.eval.runner import run_eval

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.eval
def test_golden_dataset_gates() -> None:
    report = run_eval(load_cases(ROOT / "eval" / "golden.json"), load_default_taxonomy())
    assert report.gates_passed, report.failures
    assert report.known_gaps == 2
