from dataclasses import dataclass

from jobfit.domain.extract import confirmed_skills, extract_evidence, extract_requirements
from jobfit.domain.hints import resume_hints
from jobfit.domain.model import Evidence, Requirement
from jobfit.domain.scoring import coverage, critical_gaps, gaps
from jobfit.domain.taxonomy import Taxonomy
from jobfit.logging_config import get_logger

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class Analysis:
    coverage: int
    taxonomy_version: str
    requirements: list[Requirement]
    confirmed: list[str]
    gaps: list[Requirement]
    critical_gaps: list[Requirement]
    hints: list[str]
    evidence: list[Evidence]


def analyze(vacancy: str, profile: str, taxonomy: Taxonomy) -> Analysis:
    log.info(
        "analyze start: vacancy=%d chars, profile=%d chars, taxonomy=%s",
        len(vacancy),
        len(profile),
        taxonomy.version,
    )
    requirements = extract_requirements(vacancy, taxonomy)
    evidence = extract_evidence(profile, taxonomy)
    confirmed = confirmed_skills(evidence)
    missing = gaps(requirements, confirmed)
    result = Analysis(
        coverage=coverage(requirements, confirmed),
        taxonomy_version=taxonomy.version,
        requirements=requirements,
        confirmed=sorted(confirmed),
        gaps=missing,
        critical_gaps=critical_gaps(requirements, confirmed),
        hints=resume_hints(missing),
        evidence=evidence,
    )
    log.info(
        "analyze done: coverage=%d%%, requirements=%d, confirmed=%d, gaps=%d, critical=%d",
        result.coverage,
        len(result.requirements),
        len(result.confirmed),
        len(result.gaps),
        len(result.critical_gaps),
    )
    return result
