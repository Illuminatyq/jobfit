import pytest

from jobfit.domain.extract import confirmed_skills, extract_evidence, extract_requirements
from jobfit.domain.taxonomy import Taxonomy


@pytest.mark.unit
def test_priorities_and_offers(taxonomy: Taxonomy, vacancy_text: str) -> None:
    items = {r.skill_id: r.priority for r in extract_requirements(vacancy_text, taxonomy)}
    assert items == {
        "postman": "must",
        "mysql": "must",
        "docker": "must",
        "playwright": "nice",
        "kubernetes": "nice",
    }


@pytest.mark.unit
def test_offer_section_is_ignored(taxonomy: Taxonomy, vacancy_text: str) -> None:
    ids = {r.skill_id for r in extract_requirements(vacancy_text, taxonomy)}
    assert "linux" not in ids


@pytest.mark.unit
def test_long_segment_is_not_a_header(taxonomy: Taxonomy) -> None:
    text = "Мы предлагаем хорошие условия работы, гибкий график и рабочий ноутбук на Linux."
    ids = {r.skill_id for r in extract_requirements(text, taxonomy)}
    assert "linux" in ids


@pytest.mark.unit
def test_must_wins_over_nice_on_duplicate(taxonomy: Taxonomy) -> None:
    text = "Будет плюсом: Redis.\nОбязательно: Redis."
    assert [r.priority for r in extract_requirements(text, taxonomy)] == ["must"]


@pytest.mark.unit
def test_nice_does_not_downgrade_must(taxonomy: Taxonomy) -> None:
    text = "Обязательно: Redis.\nБудет плюсом: Redis."
    assert [r.priority for r in extract_requirements(text, taxonomy)] == ["must"]


@pytest.mark.unit
def test_duties_section_is_not_a_requirement(taxonomy: Taxonomy) -> None:
    text = "Обязанности: тестировать в Postman.\nТребования: Git."
    ids = {r.skill_id for r in extract_requirements(text, taxonomy)}
    assert ids == {"git"}


@pytest.mark.unit
def test_evidence_from_profile(taxonomy: Taxonomy, profile_text: str) -> None:
    evidence = extract_evidence(profile_text, taxonomy)
    assert [item.id for item in evidence] == ["e1"]
    assert confirmed_skills(evidence) == {"postman", "mysql"}
