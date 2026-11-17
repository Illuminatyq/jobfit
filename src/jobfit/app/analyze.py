from dataclasses import dataclass

from jobfit.domain.extract import confirmed_skills, extract_evidence, extract_requirements
from jobfit.domain.hints import resume_hints
from jobfit.domain.model import Evidence, Requirement
from jobfit.domain.scoring import coverage, critical_gaps, gaps
from jobfit.domain.taxonomy import Taxonomy


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
    requirements = extract_requirements(vacancy, taxonomy)
    evidence = extract_evidence(profile, taxonomy)
    confirmed = confirmed_skills(evidence)
    missing = gaps(requirements, confirmed)
    return Analysis(
        coverage=coverage(requirements, confirmed),
        taxonomy_version=taxonomy.version,
        requirements=requirements,
        confirmed=sorted(confirmed),
        gaps=missing,
        critical_gaps=critical_gaps(requirements, confirmed),
        hints=resume_hints(missing),
        evidence=evidence,
    )
