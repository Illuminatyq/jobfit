import pytest

from jobfit.domain.taxonomy import Taxonomy
from jobfit.eval.dataset import Case
from jobfit.eval.runner import Gates, run_eval


def _case(**overrides: object) -> Case:
    base: dict[str, object] = {
        "id": "T01",
        "title": "smoke",
        "taxonomy_version": "1.0.0",
        "vacancy": "Требования:\nОбязательно: Git.\n",
        "profile": "Работаю с Git.\n",
        "expected_requirements": {"git": "must"},
        "expected_confirmed": ("git",),
        "expected_coverage": 100,
    }
    base.update(overrides)
    return Case(**base)  # type: ignore[arg-type]


@pytest.mark.unit
def test_clean_case_passes_gates(taxonomy: Taxonomy) -> None:
    report = run_eval([_case()], taxonomy)
    assert report.gates_passed
    assert report.cases[0].passed
    assert report.coverage_mae == 0.0


@pytest.mark.unit
def test_wrong_expectation_fails_gates(taxonomy: Taxonomy) -> None:
    report = run_eval([_case(expected_confirmed=("redis",))], taxonomy)
    assert not report.gates_passed
    assert any("confirmation F1" in failure for failure in report.failures)


@pytest.mark.unit
def test_known_gap_does_not_gate(taxonomy: Taxonomy) -> None:
    report = run_eval([_case(known_gap=True, expected_confirmed=("redis",))], taxonomy)
    assert report.gates_passed
    assert report.known_gaps == 1
    assert report.gating_cases == 0


@pytest.mark.unit
def test_stale_taxonomy_version_fails(taxonomy: Taxonomy) -> None:
    report = run_eval([_case(taxonomy_version="0.9.0")], taxonomy)
    assert not report.gates_passed
    assert any("устарели" in failure for failure in report.failures)


@pytest.mark.unit
def test_custom_gates_are_respected(taxonomy: Taxonomy) -> None:
    report = run_eval([_case()], taxonomy, Gates(extraction_f1=1.01))
    assert not report.gates_passed
