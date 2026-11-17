"""Deterministic resume hints derived from gaps. Pure: stdlib only."""

from jobfit.domain.model import Requirement

_MUST = "Обязательное требование вакансии. В профиле подтверждения нет — высокий риск отсева."
_NICE = "Желательное требование. Добавь, если есть реальный опыт: поднимет покрытие."


def resume_hints(items: list[Requirement]) -> list[str]:
    return [
        f"{r.name}: {_MUST if r.priority == 'must' else _NICE}"
        for r in sorted(items, key=lambda r: (r.priority != "must", r.name))
    ]
