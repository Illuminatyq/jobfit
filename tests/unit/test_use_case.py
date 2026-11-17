import json
from dataclasses import asdict

import pytest

from jobfit.app.analyze import analyze
from jobfit.domain.taxonomy import Taxonomy


@pytest.mark.unit
def test_end_to_end_deterministic(taxonomy: Taxonomy, vacancy_text: str, profile_text: str) -> None:
    first = analyze(vacancy_text, profile_text, taxonomy)
    second = analyze(vacancy_text, profile_text, taxonomy)
    assert first.coverage == 55
    assert json.dumps(asdict(first), ensure_ascii=False) == json.dumps(
        asdict(second), ensure_ascii=False
    )
