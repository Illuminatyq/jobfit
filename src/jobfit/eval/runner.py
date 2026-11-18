import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from jobfit.app.analyze import analyze
from jobfit.domain.taxonomy import Taxonomy
from jobfit.eval.dataset import Case
from jobfit.eval.metrics import PRF, accuracy, combine, prf


@dataclass(frozen=True, slots=True)
class CaseResult:
    id: str
    title: str
    known_gap: bool
    passed: bool
    deterministic: bool
    extraction: PRF
    confirmation: PRF
    priority_correct: int
    priority_total: int
    coverage_predicted: int
    coverage_expected: int
    coverage_error: int
    missing: tuple[str, ...]
    unexpected: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Gates:
    extraction_f1: float = 0.85
    confirmation_f1: float = 0.90
    priority_accuracy: float = 0.95
    coverage_mae: float = 3.0


@dataclass(frozen=True, slots=True)
class Report:
    taxonomy_version: str
    total_cases: int
    gating_cases: int
    known_gaps: int
    extraction: PRF
    confirmation: PRF
    priority_accuracy: float
    coverage_mae: float
    all_deterministic: bool
    gates_passed: bool
    failures: tuple[str, ...]
    cases: tuple[CaseResult, ...]


def run_case(case: Case, taxonomy: Taxonomy) -> CaseResult:
    first = analyze(case.vacancy, case.profile, taxonomy)
    second = analyze(case.vacancy, case.profile, taxonomy)
    predicted = {r.skill_id: r.priority for r in first.requirements}
    expected = case.expected_requirements
    extraction = prf(set(predicted), set(expected))
    shared = set(predicted) & set(expected)
    correct = sum(1 for key in shared if predicted[key] == expected[key])
    confirmation = prf(set(first.confirmed), set(case.expected_confirmed))
    error = abs(first.coverage - case.expected_coverage)
    deterministic = asdict(first) == asdict(second)
    passed = (
        extraction.f1 == 1.0
        and confirmation.f1 == 1.0
        and correct == len(shared)
        and error == 0
        and deterministic
    )
    return CaseResult(
        id=case.id,
        title=case.title,
        known_gap=case.known_gap,
        passed=passed,
        deterministic=deterministic,
        extraction=extraction,
        confirmation=confirmation,
        priority_correct=correct,
        priority_total=len(shared),
        coverage_predicted=first.coverage,
        coverage_expected=case.expected_coverage,
        coverage_error=error,
        missing=tuple(sorted(set(expected) - set(predicted))),
        unexpected=tuple(sorted(set(predicted) - set(expected))),
    )


def run_eval(cases: list[Case], taxonomy: Taxonomy, gates: Gates | None = None) -> Report:
    limits = gates or Gates()
    results = [run_case(case, taxonomy) for case in cases]
    gating = [r for r in results if not r.known_gap]
    extraction = combine([r.extraction for r in gating])
    confirmation = combine([r.confirmation for r in gating])
    priority = accuracy(
        sum(r.priority_correct for r in gating), sum(r.priority_total for r in gating)
    )
    mae = float(mean([r.coverage_error for r in gating])) if gating else 0.0
    deterministic = all(r.deterministic for r in gating)

    failures: list[str] = []
    stale = sorted({c.taxonomy_version for c in cases if c.taxonomy_version != taxonomy.version})
    if stale:
        failures.append(f"версии словаря в кейсах устарели: {', '.join(stale)}")
    if extraction.f1 < limits.extraction_f1:
        failures.append(f"extraction F1 {extraction.f1:.3f} < {limits.extraction_f1}")
    if confirmation.f1 < limits.confirmation_f1:
        failures.append(f"confirmation F1 {confirmation.f1:.3f} < {limits.confirmation_f1}")
    if priority < limits.priority_accuracy:
        failures.append(f"priority accuracy {priority:.3f} < {limits.priority_accuracy}")
    if mae > limits.coverage_mae:
        failures.append(f"coverage MAE {mae:.2f} > {limits.coverage_mae}")
    if not deterministic:
        failures.append("недетерминированный результат на гейтинг-кейсах")

    return Report(
        taxonomy_version=taxonomy.version,
        total_cases=len(results),
        gating_cases=len(gating),
        known_gaps=len(results) - len(gating),
        extraction=extraction,
        confirmation=confirmation,
        priority_accuracy=priority,
        coverage_mae=mae,
        all_deterministic=deterministic,
        gates_passed=not failures,
        failures=tuple(failures),
        cases=tuple(results),
    )


def render_markdown(report: Report) -> str:
    lines = [
        "# Eval report",
        "",
        f"Словарь: {report.taxonomy_version}",
        f"Кейсов: {report.total_cases}, гейтинг: {report.gating_cases}, "
        f"известных пробелов: {report.known_gaps}",
        "",
        "| Метрика | Значение |",
        "| --- | --- |",
        f"| extraction F1 | {report.extraction.f1:.3f} |",
        f"| confirmation F1 | {report.confirmation.f1:.3f} |",
        f"| priority accuracy | {report.priority_accuracy:.3f} |",
        f"| coverage MAE | {report.coverage_mae:.2f} |",
        f"| determinism | {'ok' if report.all_deterministic else 'FAIL'} |",
        f"| gates | {'PASS' if report.gates_passed else 'FAIL'} |",
        "",
        "| Кейс | Режим | extraction F1 | confirmation F1 | coverage | ожидание | статус |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.cases:
        mode = "known gap" if item.known_gap else "gate"
        status = "ok" if item.passed else "diff"
        lines.append(
            f"| {item.id} {item.title} | {mode} | {item.extraction.f1:.3f} "
            f"| {item.confirmation.f1:.3f} | {item.coverage_predicted} "
            f"| {item.coverage_expected} | {status} |"
        )
    if report.failures:
        lines += ["", "## Провалы гейтов", ""]
        lines += [f"- {failure}" for failure in report.failures]
    return "\n".join(lines) + "\n"


def write_reports(report: Report, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "latest.json").write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "latest.md").write_text(render_markdown(report), encoding="utf-8")
