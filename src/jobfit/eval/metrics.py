"""Pure metric math for the eval harness. Stdlib only."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PRF:
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int


def _score(tp: int, fp: int, fn: int) -> PRF:
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return PRF(precision, recall, f1, tp, fp, fn)


def prf(predicted: set[str], expected: set[str]) -> PRF:
    return _score(len(predicted & expected), len(predicted - expected), len(expected - predicted))


def combine(items: list[PRF]) -> PRF:
    return _score(sum(i.tp for i in items), sum(i.fp for i in items), sum(i.fn for i in items))


def accuracy(correct: int, total: int) -> float:
    return correct / total if total else 1.0
