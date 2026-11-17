import pytest

from jobfit.domain.extract import confirmed_skills, extract_evidence, extract_requirements
from jobfit.domain.hints import resume_hints
from jobfit.domain.scoring import WEIGHTS, coverage, critical_gaps, gaps
from jobfit.domain.taxonomy import Taxonomy


@pytest.mark.unit
def test_weighted_coverage(taxonomy: Taxonomy, vacancy_text: str, profile_text: str) -> None:
    requirements = extract_requirements(vacancy_text, taxonomy)
    confirmed = confirmed_skills(extract_evidence(profile_text, taxonomy))
    total = sum(WEIGHTS[r.priority] for r in requirements)
    matched = sum(WEIGHTS[r.priority] for r in requirements if r.skill_id in confirmed)
    assert (total, matched) == (11, 6)
    assert coverage(requirements, confirmed) == 55


@pytest.mark.unit
def test_empty_requirements_is_zero() -> None:
    assert coverage([], set()) == 0


@pytest.mark.unit
def test_empty_profile_is_zero(taxonomy: Taxonomy, vacancy_text: str) -> None:
    assert coverage(extract_requirements(vacancy_text, taxonomy), set()) == 0


@pytest.mark.unit
def test_gaps_are_sorted_must_first(taxonomy: Taxonomy, vacancy_text: str) -> None:
    requirements = extract_requirements(vacancy_text, taxonomy)
    missing = gaps(requirements, {"postman"})
    assert [r.priority for r in missing] == ["must", "must", "nice", "nice"]
    assert [r.name for r in critical_gaps(requirements, {"postman"})] == ["Docker", "MySQL"]


@pytest.mark.unit
def test_hints_follow_gap_order(taxonomy: Taxonomy, vacancy_text: str) -> None:
    requirements = extract_requirements(vacancy_text, taxonomy)
    hints = resume_hints(gaps(requirements, {"postman"}))
    assert hints[0].startswith("Docker")
    assert len(hints) == 4
