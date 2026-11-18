import pytest

from jobfit.eval.metrics import accuracy, combine, prf


@pytest.mark.unit
def test_perfect_match() -> None:
    result = prf({"a", "b"}, {"a", "b"})
    assert (result.precision, result.recall, result.f1) == (1.0, 1.0, 1.0)


@pytest.mark.unit
def test_false_positive_lowers_precision() -> None:
    result = prf({"a", "b"}, {"a"})
    assert result.precision == 0.5
    assert result.recall == 1.0


@pytest.mark.unit
def test_false_negative_lowers_recall() -> None:
    result = prf({"a"}, {"a", "b"})
    assert result.precision == 1.0
    assert result.recall == 0.5


@pytest.mark.unit
def test_both_empty_is_neutral() -> None:
    result = prf(set(), set())
    assert result.f1 == 1.0


@pytest.mark.unit
def test_disjoint_sets_score_zero() -> None:
    assert prf({"a"}, {"b"}).f1 == 0.0


@pytest.mark.unit
def test_combine_is_micro_average() -> None:
    combined = combine([prf({"a"}, {"a", "b"}), prf({"c", "d"}, {"c"})])
    assert (combined.tp, combined.fp, combined.fn) == (2, 1, 1)


@pytest.mark.unit
def test_accuracy_of_empty_is_neutral() -> None:
    assert accuracy(0, 0) == 1.0
    assert accuracy(1, 2) == 0.5
