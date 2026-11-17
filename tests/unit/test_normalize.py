import pytest

from jobfit.domain.normalize import (
    REDACTED,
    fold_homoglyphs,
    normalize,
    normalize_for_match,
    redact_pii,
)


@pytest.mark.unit
def test_nfkc_and_whitespace() -> None:
    assert normalize("  Ｐｏｓｔｍａn\n\t API  ") == "Postman API"


@pytest.mark.unit
def test_normalize_is_idempotent() -> None:
    raw = "  Java\tScript \n API "
    assert normalize(normalize(raw)) == normalize(raw)


@pytest.mark.unit
def test_pure_russian_word_is_not_folded() -> None:
    assert fold_homoglyphs("тестирование") == "тестирование"


@pytest.mark.unit
def test_mixed_script_token_is_folded() -> None:
    assert fold_homoglyphs("Jаvа") == "Java"


@pytest.mark.unit
def test_cyrillic_c_in_cpp_is_folded() -> None:
    assert fold_homoglyphs("С++") == "C++"


@pytest.mark.unit
def test_match_form_is_casefolded() -> None:
    assert normalize_for_match("Node.JS") == "node.js"


@pytest.mark.unit
def test_contacts_are_redacted() -> None:
    raw = "mail@example.com +7 (912) 209-35-91 @illumianty https://set.ki/x"
    out = redact_pii(raw)
    assert "@illumianty" not in out
    assert "mail@example.com" not in out
    assert out.count(REDACTED) == 4


@pytest.mark.unit
@pytest.mark.parametrize("text", ["Опыт 2021 2023", "Апрель 2024 — Октябрь 2026"])
def test_year_ranges_are_not_redacted(text: str) -> None:
    assert redact_pii(text) == text
