"""Precision/recall/F1 helpers for the golden-dataset evaluation gate."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Prf:
    precision: float
    recall: float
    f1: float

    def as_dict(self) -> dict[str, float]:
        return {"precision": self.precision, "recall": self.recall, "f1": self.f1}


def prf(expected: set[str], actual: set[str]) -> Prf:
    if not expected and not actual:
        return Prf(1.0, 1.0, 1.0)
    tp = len(expected & actual)
    precision = tp / len(actual) if actual else 0.0
    recall = tp / len(expected) if expected else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if precision + recall else 0.0
    return Prf(round(precision, 4), round(recall, 4), round(f1, 4))
