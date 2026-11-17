import pytest

from jobfit.domain.taxonomy import Taxonomy


def _ids(taxonomy: Taxonomy, text: str) -> set[str]:
    return {match.skill_id for match in taxonomy.find(text)}


@pytest.mark.unit
def test_java_does_not_match_javascript(taxonomy: Taxonomy) -> None:
    assert _ids(taxonomy, "Опыт с JavaScript") == {"javascript"}
    assert _ids(taxonomy, "Опыт с Java") == {"java"}


@pytest.mark.unit
def test_cyrillic_homoglyphs_are_folded(taxonomy: Taxonomy) -> None:
    assert "java" in _ids(taxonomy, "Jаvа")
    assert "cpp" in _ids(taxonomy, "С++")


@pytest.mark.unit
def test_dotnet_boundaries(taxonomy: Taxonomy) -> None:
    assert "dotnet" in _ids(taxonomy, "опыт .NET")
    assert "dotnet" not in _ids(taxonomy, "сайт example.net")


@pytest.mark.unit
def test_rest_alias_boundary(taxonomy: Taxonomy) -> None:
    assert "rest_api" in _ids(taxonomy, "REST API")
    assert "rest_api" not in _ids(taxonomy, "rest apiece")


@pytest.mark.unit
@pytest.mark.parametrize("text", ["go to market", "goto definition", "let it go"])
def test_ambiguous_go_is_rejected(taxonomy: Taxonomy, text: str) -> None:
    assert "golang" not in _ids(taxonomy, text)


@pytest.mark.unit
@pytest.mark.parametrize("text", ["Golang", "язык Go", "Go и Python"])
def test_ambiguous_go_is_accepted_with_cue(taxonomy: Taxonomy, text: str) -> None:
    assert "golang" in _ids(taxonomy, text)


@pytest.mark.unit
@pytest.mark.parametrize("text", ["docker-compose", "Docker и docker-compose"])
def test_known_limitation_nested_alias(taxonomy: Taxonomy, text: str) -> None:
    assert _ids(taxonomy, text) == {"docker", "docker_compose"}
