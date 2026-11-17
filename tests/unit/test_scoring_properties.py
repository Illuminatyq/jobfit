from random import Random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from jobfit.domain.model import Requirement
from jobfit.domain.scoring import coverage

_ids = st.sampled_from(["a", "b", "c", "d", "e", "f"])
_priorities = st.sampled_from(["must", "nice"])


@st.composite
def _requirements(draw: st.DrawFn) -> list[Requirement]:
    picked = draw(st.lists(_ids, min_size=1, max_size=6, unique=True))
    return [Requirement(skill_id=i, name=i, priority=draw(_priorities), snippet=i) for i in picked]


@pytest.mark.property
@given(_requirements(), st.lists(_ids, max_size=6))
def test_coverage_is_bounded(reqs: list[Requirement], confirmed: list[str]) -> None:
    assert 0 <= coverage(reqs, set(confirmed)) <= 100


@pytest.mark.property
@given(_requirements(), st.lists(_ids, max_size=6), _ids)
def test_coverage_is_monotone(reqs: list[Requirement], confirmed: list[str], extra: str) -> None:
    base = set(confirmed)
    assert coverage(reqs, base | {extra}) >= coverage(reqs, base)


@pytest.mark.property
@given(_requirements(), st.lists(_ids, max_size=6), st.randoms())
def test_order_does_not_matter(reqs: list[Requirement], confirmed: list[str], rng: Random) -> None:
    shuffled = list(reqs)
    rng.shuffle(shuffled)
    assert coverage(reqs, set(confirmed)) == coverage(shuffled, set(confirmed))


@pytest.mark.property
@given(_requirements(), st.lists(_ids, max_size=6))
def test_repeated_call_is_identical(reqs: list[Requirement], confirmed: list[str]) -> None:
    assert coverage(reqs, set(confirmed)) == coverage(reqs, set(confirmed))


@pytest.mark.property
@given(_requirements())
def test_full_confirmation_is_hundred(reqs: list[Requirement]) -> None:
    assert coverage(reqs, {r.skill_id for r in reqs}) == 100
